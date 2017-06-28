---
layout: default
title:  "第一个WebGL程序"
date:   2017-06-28 16:13:25 +0800
categories: 学习WebGL系列文章
---


{% include webgl-01.html %}

{% highlight javascript %}
var gl;
function initWebGL(canvas) {
  gl = null;
  
  // Try to grab the standard context. If it fails, fallback to experimental.
  gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
  
  // If we don't have a GL context, give up now
  if (!gl) {
    alert('Unable to initialize WebGL. Your browser may not support it.');
  }
  
  return gl;
}
function start() {
	var canvas = document.getElementById('glCanvas');
	gl = initWebGL(canvas);
	if (!gl) {
		return;
	}

	gl.clearColor(0.0, 1.0, 0.0, 1.0);
	gl.enable(gl.DEPTH_TEST);
	gl.depthFunc(gl.LEQUAL);
	gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
}
document.onload = function() {
	start();
}
{% endhighlight %}

