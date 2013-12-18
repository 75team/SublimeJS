//define native
function define(fn){
	fn.toString = function(){
		return 'function () { [native code] }';
	}
	return fn;
}

function mixin(des, src, map){
	if(typeof des !== 'object' 
			&& typeof des !== 'function'){
		throw new TypeError('Unable to enumerate properties of '+ des);
	}
	if(typeof src !== 'object' 
			&& typeof src !== 'function'){
		throw new TypeError('Unable to enumerate properties of '+ src);
	}

	map = map || function(d, s, i, des, src){
		//这里要加一个des[i]，是因为要照顾一些不可枚举的属性
		if(!(des[i] || (i in des))){
				return s;
		}
		return d;
	}

	if(map === true){		//override
		map = function(d,s){
				return s;
		}
	}

	for (var i in src) {
		des[i] = map(des[i], src[i], i, des, src);
		//如果返回undefined，尝试删掉这个属性
		if(des[i] === undefined) delete des[i];		
	}
	return des;				
}

function alert(obj){
	if(arguments.length < 1){
		sublime.message_dialog("");
	}
	if(obj && obj.toString()){
		sublime.message_dialog(obj.toString());
	}else{
		if(obj === undefined){
			sublime.message_dialog("undefined");
		}
		if(obj === null){
			sublime.message_dialog("null");
		}
	}
}

global.__commands = {};

function defineCommand(name, type, handler){
	if(typeof(type) == 'function'){
		handler = type;
		type = 'TextCommand';
	}
	global.__commands[name.toLowerCase()] = handler;
	global.registerCommand(name, type);
}

function runCommand(command){
	var handler = global.__commands[command],
		args = [].slice.call(arguments, 1);

	if(handler){
		handler.apply(global, args);
	}else{
		handler = require('../../' + command + '.command');
		handler.apply(global, args);			
	}
}

mixin(global, {
	alert: define(alert),
	mixin: define(mixin),
	defineCommand: define(defineCommand),
	runCommand: define(runCommand)
});

//============================================
var EventEmitter = require('events').EventEmitter;
global.E = new EventEmitter();
global.E.on('post_save', function(view){
	var file = view.file_name();
	for(var filename in global.__modules){
		var shortname = filename.split('Packages').slice(-1) 
		if(file.indexOf(shortname) >= 0){
			global.reload();
			return;
		}
	}
});

global.E.on_query_completions = function(){
	/* This Event must by called Sync */
	return [];
}

sublime.E = global.E;

var _timers = [];

function setTimeout(callback, delay){
	_timers.push(callback);
	var timerId = _timers.length;
	sublime.set_timeout(function(){
		var handler = _timers[timerId - 1];
		if(handler){
			handler();
		}
	}, delay);
	return timerId;
}

function clearTimeout(timerId){
	_timers[timerId - 1] = null;
}

function setInterval(callback, delay){
	_timers.push(callback);
	var timerId = _timers.length;
	sublime.set_timeout(function(){
		var handler = _timers[timerId - 1];
		if(handler){
			handler();
			sublime.set_timeout(arguments.callee, delay);
		}
	}, delay);
	return timerId;	
}

var clearInterval = clearTimeout;

function nextTick(t) { setTimeout(t, 0); };

function load_settings(setting){

}

mixin(global, {
	setTimeout: define(setTimeout),
	setInterval: define(setInterval),
	clearTimeout: define(clearTimeout),
	clearInterval: define(clearInterval),
	nextTick: define(nextTick)
});

global.when=require('when');

var fs = require('fs');

/*fs.stat(sublime.packages_path(), function(err, stats){
	console.log(stats);
});
console.log('ok');*/

var plugins = fs.readdirSync(sublime.packages_path());
plugins = plugins.concat(fs.readdirSync(sublime.installed_packages_path()));
plugins.forEach(function(plugin){
	if(plugin !== '.DS_Store'){
		var basedir = sublime.packages_path() + '/' + plugin + '/';
		try{
			var conf = load_resource(basedir + 'package.json');
			var jsboot = conf.main || 'index.js';
			load_js_file(basedir + jsboot);
		}catch(ex){
			//console.log(ex + ' ' + loader);
		}
	}
});

/*var http = require('http');

http.get("http://www.baidu.com", function(res){
	console.log(res.read());
});*/
