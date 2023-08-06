(function() { function concat() {
  console.log(arguments);
}

function cat() {
  console.log("hello world");
}

function test() {
  alert('this is a test');
}
window.JST = window.JST || {};
var template = function(str){var fn = new Function('obj', 'var __p=[],print=function(){__p.push.apply(__p,arguments);};with(obj||{}){__p.push(\''+str.replace(/\\/g, '\\\\').replace(/'/g, "\\'").replace(/<%=([\s\S]+?)%>/g,function(match,code){return "',"+code.replace(/\\'/g, "'")+",'";}).replace(/<%([\s\S]+?)%>/g,function(match,code){return "');"+code.replace(/\\'/g, "'").replace(/[\r\n\t]/g,' ')+"__p.push('";}).replace(/\r/g,'\\r').replace(/\n/g,'\\n').replace(/\t/g,'\\t')+"');}return __p.join('');");return fn;};
window.JST['photo_detail'] = template('<div class="photo">\n <img src="<%= src %>" />\n <div class="caption">\n  <%= caption %> by <%= author %>\n </div>\n</div>');
window.JST['photo_list'] = template('<div class="photo">\n <img src="<%= src %>" />\n <div class="caption">\n  <%= caption %>\n </div>\n</div>');
window.JST['video_detail'] = template('<div class="video">\n <video src="<%= src %>" />\n <div class="caption">\n  <%= description %>\n </div>\n</div>');
 }).call(this);