---
layout: post
title: iOS特效之破碎的ViewController
date: 2017-08-23 13:30:59 +0800
categories: iOS开发
---

### [点击获取本文示例代码](https://github.com/SquarePants1991/BrokenGlassEffect){:target="_blank"}，本文代码在分支transition中。

### 前言
我们在[iOS特效之你家玻璃碎了](http://www.gltech.win/ios%E5%BC%80%E5%8F%91/2017/08/22/iOS%E7%89%B9%E6%95%88%E4%B9%8B%E4%BD%A0%E5%AE%B6%E7%8E%BB%E7%92%83%E7%A2%8E%E4%BA%86.html){:target="_blank"} 中介绍了一个没什么🥚用的破碎效果，在这篇文章中我将把它用在ViewController的dismiss过渡动画中。效果如下，我调整了点的大小，食用效果更佳。不过要注意的是，不要在debug环境下把点的大小调整到15以下，否则你的机器可能承受不了，FPS也许会降到10以下。想要更小的点，则需要在release环境下编译。下面是调整点大小的相关代码。
```swift
 private func buildPointData() -> [Float] {
  ...
        let pointSize: Float = 2
  ...
}
```

![](http://upload-images.jianshu.io/upload_images/2949750-a80162b3e4f4bd19.jpg?imageMogr2/auto-orient/strip)

### 原理
使用苹果提供的自定义ViewController过渡动画技术，可以很方便的将`BrokenGlassEffectView`植入到过渡动画中。将要被dismiss掉的ViewController渲染到一张图片上，传递给`BrokenGlassEffectView`，然后使用这张图片做破碎的动画，这样就可以产生ViewController破碎的效果了。

### 实现自定义ViewController过渡动画
想要实现自定义过渡动画，首先要实现一个动画管理类，这个类控制着过渡动画如何进行。本文的动画控制类在`BrokenGlassTransitionAnimator.swift`中。下面是动画的核心代码。
```swift
func animateTransition(using transitionContext: UIViewControllerContextTransitioning) {
    let containerView = transitionContext.containerView
    guard let fromVC = transitionContext.viewController(forKey: UITransitionContextViewControllerKey.from),
        let toVC = transitionContext.viewController(forKey: UITransitionContextViewControllerKey.to) else {
            return
    }
    let snapshotImage = createImage(layer: fromVC.view.layer)
    let brokenGlassView = BrokenGlassEffectView.init(frame: fromVC.view.bounds)
    fromVC.view.removeFromSuperview()
    containerView.addSubview(toVC.view)
    containerView.addSubview(brokenGlassView)
    brokenGlassView.setImageForBroke(image: snapshotImage)
    brokenGlassView.beginBroke()
    DispatchQueue.main.asyncAfter(deadline: .now() + 1.2) { [weak brokenGlassView] in
        brokenGlassView?.removeFromSuperview()
        brokenGlassView?.destroy()
        transitionContext.completeTransition(!transitionContext.transitionWasCancelled)
    }
}
```
`transitionContext`为我们提供了过渡的来源VC，目的VC，动画执行的容器View。我们要做的是dismiss动画，所以先把目的VC的View加入容器View，再把`BrokenGlassEffectView`加入容器View，给来源VC截图，通过`setImageForBroke`传递给`BrokenGlassEffectView`。我通过经验给了一个1.2的动画结束时间，你也可以通过计算最慢的一个点到达底部的时间来确定动画时间，使用位移和加速度的物理公式，可以计算出来动画时间。
![](http://upload-images.jianshu.io/upload_images/2949750-709291fee5ccb8c6.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
本文y轴的初始速度是0，所以公式可以简化为`s=at*t*0.5`，位移s最远为2，a最小为3，`let yAccelerate = (-Float(arc4random()) / Float(RAND_MAX)) * 1.5 - 3.0`，所以我们可以计算出t=1.154s。由于我们限制了y轴最大速度为6，因此可以计算出到达最大速度最多需要6/3 = 2s，最少需要6/4.5 = 1.33s，也就是说所有的点离开屏幕时都没有到达最大速度，所以t=1.154s没有任何问题。

### VC截图
在给VC截图时我偷懒没有在Y轴上翻转图片。
```swift
func createImage(layer: CALayer) -> UIImage {
    let bitsPerComponent = 8
    let bytesPerPixel = 4
    let width:Int = Int(layer.bounds.size.width)
    let height:Int = Int(layer.bounds.size.height)
    let imageData = UnsafeMutableRawPointer.allocate(bytes: Int(width * height * bytesPerPixel), alignedTo: 8)
    
    let colorSpace = CGColorSpaceCreateDeviceRGB()
    let imageContext = CGContext.init(data: imageData, width: width, height: height, bitsPerComponent: bitsPerComponent, bytesPerRow:
width * bytesPerPixel, space: colorSpace, bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue |
CGImageByteOrderInfo.order32Big.rawValue )
    layer.render(in: imageContext!)
    
    let cgImage = imageContext?.makeImage()
    let image = UIImage.init(cgImage: cgImage!)
    return image
}
```
因此我移除了Fragment Shader里的UV翻转。` uv = float2(uv[0], uv[1]);`。
```c
fragment float4 passThroughFragment(VertexOut inFrag [[stage_in]],
                                    float2 pointCoord  [[point_coord]],
                                     texture2d<float> diffuse [[ texture(0) ]],
                                    const device Uniforms& uniforms [[ buffer(0) ]])
{
    float2 additionUV = float2((pointCoord[0]) * uniforms.pointTexcoordScale[0], (1.0 - pointCoord[1]) * uniforms.pointTexcoordScale[1]);
    float2 uv = inFrag.pointPosition + additionUV;
    uv = float2(uv[0], uv[1]);
    float4 finalColor = diffuse.sample(s, uv);
    return finalColor;
};
```

### 使用自定义过渡
例子中有两个VC，我在第一个VC中实现了`UIViewControllerTransitioningDelegate`，并且为dismiss动画提供了动画控制类实例。
```swift
let brokenGlassAnimator: BrokenGlassTransitionAnimator = BrokenGlassTransitionAnimator.init()
...
func animationController(forDismissed dismissed: UIViewController) -> UIViewControllerAnimatedTransitioning? {
    return brokenGlassAnimator
}
```
在跳转时将要跳转到的VC的transitioningDelegate设为第一个VC，这样它dismiss时就会使用`brokenGlassAnimator`了。
```swift
let vc = PresentedViewController.instance()
vc.transitioningDelegate = self
self.present(vc, animated: true) {
    
}
```

### 总结
本文利用了自定义ViewController过渡动画的特性，将破碎动画融入到dismiss动画里。这篇和上一篇文章提供了制作基于Metal的VC过渡动画的思路，按照这个思路，发挥想象力就可以做出更多炫酷的过渡动画了。
