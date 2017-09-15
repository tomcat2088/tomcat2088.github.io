---
layout: post
title: ShadowMap(二)
date: 2017-08-24 15:26:35 +0800
categories: 学习OpenGLES系列文章
---

### [获取示例代码](https://github.com/SquarePants1991/OpenGLESLearn)，本文代码在分支chapter23中。
***

本文将为大家解决上一篇文章留下来的问题。

### Shadow acne
在上一篇文末，我们看到了有问题的阴影效果，我们常把这种问题称为Shadow acne，在不该出现阴影的地方出现了亮暗相间的条纹。我们通过下面这张图解释产生问题的原因。
![](http://upload-images.jianshu.io/upload_images/2949750-97591949f22a8a70.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
黄色部分代表从深度纹理获取到的深度值，因为纹理是有分辨率限制的，不同位置的相邻像素点会采样到同一个深度值。比如三个深度值分别为0.6，0.7，0.8的像素点，没有像素点遮挡它们，但是他们采样到的深度值可能都是0.7，那么深度为0.8的像素点就会变暗。我们可以通过增加采样到的深度值的方法避免这个问题。我们把增加的值称为`shadow bias`。对应的Fragment Shader代码如下。我们将采样到的深度值`shadowColor.r`增加`0.005`再做比较。
```c
if (shadowUV.x >= 0.0 && shadowUV.x <=1.0 && shadowUV.y >= 0.0 && shadowUV.y <=1.0) {
    vec4 shadowColor = texture2D(shadowMap, shadowUV);
    if (shadowColor.r + 0.005 < positionInLightSpace.z) {
        shadow = 0.1;
    } else {
        shadow = 1.0;
    }
}
```
修复后效果如下。
![](http://upload-images.jianshu.io/upload_images/2949750-1e6169c9e4e06490.jpg?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
因为面的法线不同，需要调整的深度值也不一样，一般会把bias设置成与法线相关的一个值。
```c
float bias = 0.005*tan(acos(dot(transformedNormal, normalizedLightDirection)));
bias = clamp(bias, 0.0, 0.01);
...
if (shadowColor.r + bias < positionInLightSpace.z) {
...
}
...
```

### Peter Panning
我们看上面的效果图会发现影子和物体有一段偏移量，我们一般称这种现象为Peter Panning，正如彼得·潘故事里的主人公和影子分离的现象。
![](http://upload-images.jianshu.io/upload_images/2949750-d07cba01a8770339.jpeg?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
想要修复这个问题，可以提高深度纹理的精度。我们在设置光源投影矩阵的时候，nearPlane和farPlane都设置的比较大，这导致了深度纹理需要表达更大范围的值，从而丧失了精度。
```objectivec
self.lightProjectionMatrix = GLKMatrix4MakeOrtho(-10, 10, -10, 10, -100, 100);
```
我们将它修改成如下数据。
```objectivec
self.lightProjectionMatrix = GLKMatrix4MakeOrtho(-10, 10, -10, 10, 0.1, 28);
```
效果就会好很多。

![](http://upload-images.jianshu.io/upload_images/2949750-91f2e166216e47f3.jpg?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

### 软阴影
现在的阴影看起来还可以，不过边缘会有些锯齿。真实的阴影边缘往往比较柔和，我们可以通过多重采样让阴影变得柔和。
```c
if (shadowUV.x >= 0.0 && shadowUV.x <=1.0 && shadowUV.y >= 0.0 && shadowUV.y <=1.0) {
    vec2 texelSize = 1.0 / vec2(1024, 1024);
    for(int x = -1; x <= 1; ++x)
    {
        for(int y = -1; y <= 1; ++y)
        {
            float pcfDepth = texture2D(shadowMap, shadowUV + vec2(x, y) * texelSize).r;
            shadow += positionInLightSpace.z - bias < pcfDepth ? 0.6 : 0.0;
        }
    }
    shadow /= 9.0;
}
```
`vec2(1024, 1024)`是阴影贴图的大小，你也可以通过uniform把贴图大小传递进来。通过采样相邻点的深度值，判断是否需要阴影，然后求出平均值，从而达到平滑的效果。效果如下。
![](http://upload-images.jianshu.io/upload_images/2949750-d40e1af0236689fa.jpg?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

### 处理未被阴影贴图覆盖的区域
目前我们的算法有一个瑕疵，你所看见的区域有可能不会全部被阴影贴图覆盖到，我们把下面的正方体变大就可以看到问题。floor的大小改为30，1，30。
```objectivec
- (void)createFloor {
    UIImage *normalImage = [UIImage imageNamed:@"stoneFloor_NRM.png"];
    GLKTextureInfo *normalMap = [GLKTextureLoader textureWithCGImage:normalImage.CGImage options:nil error:nil];
    UIImage *diffuseImage = [UIImage imageNamed:@"stoneFloor.jpg"];
    GLKTextureInfo *diffuseMap = [GLKTextureLoader textureWithCGImage:diffuseImage.CGImage options:nil error:nil];
    
    NSString *cubeObjFile = [[NSBundle mainBundle] pathForResource:@"cube" ofType:@"obj"];
    WavefrontOBJ *cube = [WavefrontOBJ objWithGLContext:self.glContext objFile:cubeObjFile diffuseMap:diffuseMap normalMap:normalMap];
    cube.modelMatrix = GLKMatrix4Multiply(GLKMatrix4MakeTranslation(0, -1, 0), GLKMatrix4MakeScale(30, 1, 30 ));
    [self.objects addObject:cube];
}
```
效果如下。未被阴影贴图覆盖的区域都是黑色的。
![](http://upload-images.jianshu.io/upload_images/2949750-245305feb067973c.jpg?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
我们只要在Fragment Shader中添加一个分支条件就可以解决这个问题。
```c
if (shadowUV.x >= 0.0 && shadowUV.x <=1.0 && shadowUV.y >= 0.0 && shadowUV.y <=1.0) {
    vec2 texelSize = 1.0 / vec2(1024, 1024);
    for(int x = -1; x <= 1; ++x)
    {
        for(int y = -1; y <= 1; ++y)
        {
            float pcfDepth = texture2D(shadowMap, shadowUV + vec2(x, y) * texelSize).r;
            shadow += positionInLightSpace.z - bias < pcfDepth ? 1.0 : 0.0;
        }
    }
    shadow /= 9.0;
} else {
    shadow = 1.0;
}
```
![](http://upload-images.jianshu.io/upload_images/2949750-cfca1b928d9c6eac.jpg?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

最后我们打开法线贴图，效果如下。
![](http://upload-images.jianshu.io/upload_images/2949750-fa3e61011cdeb6ca.jpg?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

### What‘s Next？
ShadowMap的两篇文章主要介绍了ShadowMap的基本原理和常见问题的修复思路，除了这些之外还有其他更加复杂的优化和解决issus的方案。想要继续深入了解，可以参考[常用的ShadowMap问题解决方案](https://msdn.microsoft.com/en-us/library/windows/desktop/ee416324%28v=vs.85%29.aspx)，以及它的底部标明的引用的文章。

### 本文参考的文章列表
[Shadow Mapping](https://learnopengl.com/#!Advanced-Lighting/Shadows/Shadow-Mapping)
[Common Techniques to Improve Shadow Depth Maps](https://msdn.microsoft.com/en-us/library/windows/desktop/ee416324%28v=vs.85%29.aspx)
