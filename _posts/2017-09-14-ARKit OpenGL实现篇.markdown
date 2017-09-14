---
layout: post
title: ARKit OpenGL实现篇
date: 2017-09-14 09:43:46 +0800
categories: iOS开发
---

### [获取示例代码](https://github.com/SquarePants1991/OpenGLESLearn){:target="_blank"}，本文代码在分支ARKit中。
***

> 如果你想了解ATRKit的基础知识，请访问[ARKit原理篇](http://www.gltech.win/ios%E5%BC%80%E5%8F%91/2017/09/14/ARKit%E5%8E%9F%E7%90%86%E7%AF%87.html){:target="_blank"}


> 本文所用OpenGL基础代码来自[OpenGL ES系列](http://www.jianshu.com/p/df4c8f9bc08d)，具备渲染几何体，纹理等基础功能，实现细节将不赘述。

集成ARKit的关键代码都在`ARGLBaseViewController`中。我们来看一下它的代码。
### 处理ARFrame
```objc
- (void)session:(ARSession *)session didUpdateFrame:(ARFrame *)frame {
    // 同步YUV信息到 yTexture 和 uvTexture
    CVPixelBufferRef pixelBuffer = frame.capturedImage;
    GLsizei imageWidth = (GLsizei)CVPixelBufferGetWidthOfPlane(pixelBuffer, 0);
    GLsizei imageHeight = (GLsizei)CVPixelBufferGetHeightOfPlane(pixelBuffer, 0);
    void * baseAddress = CVPixelBufferGetBaseAddressOfPlane(pixelBuffer, 0);
    
    glBindTexture(GL_TEXTURE_2D, self.yTexture);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_LUMINANCE, imageWidth, imageHeight, 0, GL_LUMINANCE, GL_UNSIGNED_BYTE, baseAddress);
    glBindTexture(GL_TEXTURE_2D, 0);
    
    imageWidth = (GLsizei)CVPixelBufferGetWidthOfPlane(pixelBuffer, 1);
    imageHeight = (GLsizei)CVPixelBufferGetHeightOfPlane(pixelBuffer, 1);
    void *laAddress = CVPixelBufferGetBaseAddressOfPlane(pixelBuffer, 1);
    glBindTexture(GL_TEXTURE_2D, self.uvTexture);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_LUMINANCE_ALPHA, imageWidth, imageHeight, 0, GL_LUMINANCE_ALPHA, GL_UNSIGNED_BYTE, laAddress);
    glBindTexture(GL_TEXTURE_2D, 0);
    
    self.videoPlane.yuv_yTexture = self.yTexture;
    self.videoPlane.yuv_uvTexture = self.uvTexture;
    [self setupViewport: CGSizeMake(imageHeight, imageWidth)];
    
    // 同步摄像机
    matrix_float4x4 cameraMatrix = matrix_invert([frame.camera transform]);
    GLKMatrix4 newCameraMatrix = GLKMatrix4Identity;
    for (int col = 0; col < 4; ++col) {
        for (int row = 0; row < 4; ++row) {
            newCameraMatrix.m[col * 4 + row] = cameraMatrix.columns[col][row];
        }
    }
    
    self.cameraMatrix = newCameraMatrix;
    GLKVector3 forward = GLKVector3Make(-self.cameraMatrix.m13, -self.cameraMatrix.m23, -self.cameraMatrix.m33);
    GLKMatrix4 rotationMatrix = GLKMatrix4MakeRotation(M_PI / 2, forward.x, forward.y, forward.z);
    self.cameraMatrix = GLKMatrix4Multiply(rotationMatrix, newCameraMatrix);
}
```
上面的代码展示了如何处理ARKit捕捉的ARFrame，`ARFrame`的`capturedImage`存储了摄像头捕捉的图片信息，类型是`CVPixelBufferRef`。默认情况下，图片信息的格式是YUV，通过两个`Plane`来存储，也可以理解为两张图片。一张格式是Y（Luminance），保存了明度信息，另一张是UV（Chrominance、Chroma），保存了色度和浓度。我们需要把这两张图分别绑定到不同的纹理上，然后在Shader中利用算法将YUV转换成RGB。下面是处理纹理的Fragment Shader，利用公式进行颜色转换。
```c
precision highp float;

varying vec3 fragNormal;
varying vec2 fragUV;

uniform float elapsedTime;
uniform mat4 normalMatrix;
uniform sampler2D yMap;
uniform sampler2D uvMap;

void main(void) {
    vec4 Y_planeColor = texture2D(yMap, fragUV);
    vec4 CbCr_planeColor = texture2D(uvMap, fragUV);
    
    float Cb, Cr, Y;
    float R ,G, B;
    Y = Y_planeColor.r * 255.0;
    Cb = CbCr_planeColor.r * 255.0 - 128.0;
    Cr = CbCr_planeColor.a * 255.0 - 128.0;
    
    R = 1.402 * Cr + Y;
    G = -0.344 * Cb - 0.714 * Cr + Y;
    B = 1.772 * Cb + Y;
    
    
    vec4 videoColor = vec4(R / 255.0, G / 255.0, B / 255.0, 1.0);
    gl_FragColor = videoColor;
}
```

处理并绑定好纹理后，为了保证不同屏幕尺寸下，纹理不被非等比拉伸，所以对`viewport`进行重了新计算`[self setupViewport: CGSizeMake(imageHeight, imageWidth)];`。接下来将ARKit计算出来的摄像机的变换赋值给`self.cameraMatrix`。注意ARKit捕捉的图片需要旋转90度后才能正常显示，所以在设置Viewport时特意颠倒了宽和高，并在最后对摄像机进行了旋转。

### VideoPlane
VideoPlane是为了显示视频编写的几何体，它能够接收两个纹理，Y和UV。
```objc
@interface VideoPlane : GLObject
@property (assign, nonatomic) GLuint yuv_yTexture;
@property (assign, nonatomic) GLuint yuv_uvTexture;
- (instancetype)initWithGLContext:(GLContext *)context;
- (void)update:(NSTimeInterval)timeSinceLastUpdate;
- (void)draw:(GLContext *)glContext;
@end

...

- (void)draw:(GLContext *)glContext {
    [glContext setUniformMatrix4fv:@"modelMatrix" value:self.modelMatrix];
    bool canInvert;
    GLKMatrix4 normalMatrix = GLKMatrix4InvertAndTranspose(self.modelMatrix, &canInvert);
    [glContext setUniformMatrix4fv:@"normalMatrix" value:canInvert ? normalMatrix : GLKMatrix4Identity];
    [glContext bindTextureName:self.yuv_yTexture to:GL_TEXTURE0 uniformName:@"yMap"];
    [glContext bindTextureName:self.yuv_uvTexture to:GL_TEXTURE1 uniformName:@"uvMap"];
    [glContext drawTrianglesWithVAO:vao vertexCount:6];
}
```
其他的功能很简单，就是绘制一个正方形，最终配合显示视频的Shader，渲染YUV格式的数据。

### 透视投影矩阵
在ARFrame可以获取渲染需要的纹理和摄像机矩阵，除了这些，和真实摄像头匹配的透视投影矩阵也是必须的。它能够让渲染出来的3D物体透视看起来很自然。
```objc
- (void)session:(ARSession *)session cameraDidChangeTrackingState:(ARCamera *)camera {
    matrix_float4x4 projectionMatrix = [camera projectionMatrixWithViewportSize:self.viewport.size orientation:UIInterfaceOrientationPortrait zNear:0.1 zFar:1000];
    GLKMatrix4 newWorldProjectionMatrix = GLKMatrix4Identity;
    for (int col = 0; col < 4; ++col) {
        for (int row = 0; row < 4; ++row) {
           newWorldProjectionMatrix.m[col * 4 + row] = projectionMatrix.columns[col][row];
        }
    }
    self.worldProjectionMatrix = newWorldProjectionMatrix;
}
```
上面的代码演示了如何通过ARKit获取3D透视投影矩阵，有了透视投影矩阵和摄像机矩阵，就可以很方便的利用OpenGL渲染物体了。
```objc
- (void)glkView:(GLKView *)view drawInRect:(CGRect)rect {
    [super glkView:view drawInRect:rect];
    
    [self.objects enumerateObjectsUsingBlock:^(GLObject *obj, NSUInteger idx, BOOL *stop) {
        [obj.context active];
        [obj.context setUniform1f:@"elapsedTime" value:(GLfloat)self.elapsedTime];
        [obj.context setUniformMatrix4fv:@"projectionMatrix" value:self.worldProjectionMatrix];
        [obj.context setUniformMatrix4fv:@"cameraMatrix" value:self.cameraMatrix];
        
        [obj.context setUniform3fv:@"lightDirection" value:self.lightDirection];
        [obj draw:obj.context];
    }];
}
```

本文主要介绍了OpenGL ES渲染ARKit的基本思路，没有对OpenGL ES技术细节描述太多。如果你有兴趣，可以直接clone [Github](https://github.com/SquarePants1991/OpenGLESLearn)上的代码深入了解。
