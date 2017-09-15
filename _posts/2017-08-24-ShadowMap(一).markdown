---
layout: post
title: ShadowMap(一)
date: 2017-08-24 15:26:05 +0800
categories: 学习OpenGLES系列文章
---

### [获取示例代码](https://github.com/SquarePants1991/OpenGLESLearn)，本文代码在分支chapter22中。
***

本文将为大家介绍3D实时阴影技术ShadowMap，又称为阴影贴图技术。下面是效果图。
![](http://upload-images.jianshu.io/upload_images/2949750-817e73f1c6cde7ae.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
![](http://upload-images.jianshu.io/upload_images/2949750-219778296d77cefc.jpg?imageMogr2/auto-orient/strip)

### 原理介绍
我们在了解ShadowMap这项技术之前，先来了解一下什么是阴影。在现实生活中，阴影伴随着光而生。下面这张图演示了在平行光下，影子是如何形成的。

![](http://upload-images.jianshu.io/upload_images/2949750-a97ad3f8c3f7b434.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

图中的两个物体，在光照方向上，距离光源最近的那些点会被照亮，之后的点则不会接受到光照。所以判断一个点是否在阴影中的关键就是，它是否是光照方向上距离光源最近的点。

### 深度缓冲区
之前我们说过深度缓冲区，他可以用来判断像素是否需要被写入颜色缓冲区。它的原理如下。
1. 初始化所有的深度缓冲区数据为1。
1. 系统在每个像素写入颜色缓冲区之前都会比较它的深度值和当前深度缓冲区对应的深度值，如果小于当前深度缓冲区对应的深度值，就写入该像素，并将当前深度缓冲区对应的深度值改为该像素的深度值。否则，丢弃该像素。

所有的深度值在比较前都会被规范化成0~1，投影矩阵近平面上的深度为0，远平面上的深度为1。最终保留下来的都是深度最小的像素点。我们可以利用这个特性来记录光照方向上距离光源最近的点。

### 深度纹理
我们如果使用纹理来充当深度缓冲区，那么我们将得到深度纹理。深度纹理是我们找到光照方向上距离光源最近的点的好帮手。假设我们在光源出放置一个摄像机，观察方向和光源方向调整为一致。然后使用正交投影矩阵进行投影。接着使用这个摄像机渲染场景。那么深度纹理中就会记录一系列距离光源最近的像素点的深度值。

### 使用深度纹理
我们有了深度纹理，那么如何使用它呢？在使用它之前我们需要明白像素点的坐标和深度纹理UV的对应关系。当我们使用光源的VP矩阵和模型矩阵变换像素点的原始坐标之后，坐标值便落在了-1到1之间。我们把坐标加上1再乘以0.5，xy就可以当做UV使用。使用xy在深度纹理上取值，就可以得到这个像素点所对应的距离光源最近的点的深度值。将这个深度值与前面经过处理的像素坐标的z轴值比较，就可以判断该像素点是否在阴影中。

### Fragment Shader
为了配合Shadow Map，Fragment Shader需要做以下改变。
1. 添加深度纹理和光源处的VP矩阵。
```c
uniform mat4 lightMatrix;
uniform sampler2D shadowMap;
```

1. 获取深度纹理上对应的深度值并和当前深度值做判断，如果当前深度比距离光源最近的点深度大，则在阴影中，否则不在。经过处理的像素坐标的z轴可以作为当前深度值。它的范围在0到1之间。
```c
float shadow = 0.0;
vec4 positionInLightSpace = lightMatrix * modelMatrix * vec4(fragPosition, 1.0);
positionInLightSpace /= positionInLightSpace.w;
positionInLightSpace = (positionInLightSpace + 1.0) * 0.5;
vec2 shadowUV = positionInLightSpace.xy;
if (shadowUV.x >= 0.0 && shadowUV.x <=1.0 && shadowUV.y >= 0.0 && shadowUV.y <=1.0) {
    vec4 shadowColor = texture2D(shadowMap, shadowUV);
    if (shadowColor.r < positionInLightSpace.z) {
        shadow = 0.1;
    } else {
        shadow = 1.0;
    }
}
```
1. 为漫反射颜色加入阴影系数shadow的影响，shadow为1时，无影响，值越小，颜色越暗。
```c
vec3 diffuse = diffuseStrength * light.color * texture2D(diffuseMap, fragUV).rgb * light.indensity * shadow;
```

### 生成深度纹理
想要生成光源处VP矩阵下的深度纹理，需要以下操作。
##### 生成带有深度纹理的Framebuffer。

```objectivec
- (void)createShadowMap {
    self.shadowMapSize = CGSizeMake(1024, 1024);
    glGenFramebuffers(1, &shadowMapFramebuffer);
    glBindFramebuffer(GL_FRAMEBUFFER, shadowMapFramebuffer);
    // 生成深度缓冲区的纹理对象并绑定到framebuffer上
    glGenTextures(1, &shadowDepthMap);
    glBindTexture(GL_TEXTURE_2D, shadowDepthMap);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT, self.shadowMapSize.width, self.shadowMapSize.height, 0, GL_DEPTH_COMPONENT, GL_UNSIGNED_INT, NULL);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT , GL_TEXTURE_2D, shadowDepthMap, 0);
    GLenum status = glCheckFramebufferStatus(GL_FRAMEBUFFER);
    if (status != GL_FRAMEBUFFER_COMPLETE) {
        // framebuffer生成失败
    }
    glBindFramebuffer(GL_FRAMEBUFFER, 0);
}
```

将`GL_DEPTH_COMPONENT`深度格式的纹理贴图作为Framebuffer的深度缓冲区附件，所有渲染到深度缓冲区的数据都会被写入`shadowDepthMap`。

#####  使用光源的VP渲染场景到上面的Framebuffer。因为我们只需要深度数据，所以可以新建一个Fragment Shader来渲染场景。一个空的`Fragment Shader`就足够了，因为深度会默认写入深度缓冲区，不需要任何处理。
```c
precision highp float;

void main(void) {
    
}
```
然后使用光源的VP渲染。`lightProjectionMatrix`和`lightCameraMatrix`分别是光源的投影和观察矩阵。到此我们就得到了光源空间的深度纹理了。
```objectivec
- (void)glkView:(GLKView *)view drawInRect:(CGRect)rect {
    glBindFramebuffer(GL_FRAMEBUFFER, shadowMapFramebuffer);
    glViewport(0, 0, self.shadowMapSize.width, self.shadowMapSize.height);
    glClearColor(0.7, 0.7, 0.7, 1);
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    [self drawObjectsForShadowMap];
    
    ...
}

- (void)drawObjectsForShadowMap {
    [self.objects enumerateObjectsUsingBlock:^(GLObject *obj, NSUInteger idx, BOOL *stop) {
        [self.shadowMapContext active];
        [obj.context setUniformMatrix4fv:@"projectionMatrix" value:self.lightProjectionMatrix];
        [obj.context setUniformMatrix4fv:@"cameraMatrix" value:self.lightCameraMatrix];
        [obj draw:self.shadowMapContext];
    }];
}
```

### 绘制主场景
接下来我们来绘制场景到屏幕。
```objectivec
- (void)glkView:(GLKView *)view drawInRect:(CGRect)rect {
    ...
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    [self drawObjectsForShadowMap];
    
    [(GLKView *)(self.view) bindDrawable];
    glClearColor(0.7, 0.7, 0.7, 1);
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    [self drawObjects];
}
```
在`[self drawObjects];`中，我们将深度纹理传入Fragment Shader，而且还要传入光源的VP矩阵。
```objectivec
- (void)drawObjects {
    [self.objects enumerateObjectsUsingBlock:^(GLObject *obj, NSUInteger idx, BOOL *stop) {
        [obj.context active];
        [obj.context setUniform1f:@"elapsedTime" value:(GLfloat)self.elapsedTime];
        [obj.context setUniformMatrix4fv:@"projectionMatrix" value:self.projectionMatrix];
        [obj.context setUniformMatrix4fv:@"cameraMatrix" value:self.cameraMatrix];
        [obj.context setUniform3fv:@"eyePosition" value:self.eyePosition];
        [obj.context setUniform3fv:@"light.direction" value:self.light.direction];
        [obj.context setUniform3fv:@"light.color" value:self.light.color];
        [obj.context setUniform1f:@"light.indensity" value:self.light.indensity];
        [obj.context setUniform1f:@"light.ambientIndensity" value:self.light.ambientIndensity];
        [obj.context setUniform3fv:@"material.diffuseColor" value:self.material.diffuseColor];
        [obj.context setUniform3fv:@"material.ambientColor" value:self.material.ambientColor];
        [obj.context setUniform3fv:@"material.specularColor" value:self.material.specularColor];
        [obj.context setUniform1f:@"material.smoothness" value:self.material.smoothness];
        
        [obj.context setUniform1i:@"useNormalMap" value:self.useNormalMap];
        
        [obj.context setUniformMatrix4fv:@"lightMatrix" value:GLKMatrix4Multiply(self.lightProjectionMatrix, self.lightCameraMatrix)];
        [obj.context bindTextureName:shadowDepthMap to:GL_TEXTURE2 uniformName:@"shadowMap"];
        
        [obj draw:obj.context];
    }];
}
```

到此，阴影贴图的主要原理和实现就介绍完了，但是此时如果你运行代码将会得到这样的场景。这是ShadowMap本身的实现技术带来的问题，我将会在下一篇文章中介绍修复的方案。
![](http://upload-images.jianshu.io/upload_images/2949750-f82bda82c5b476b3.jpg?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
