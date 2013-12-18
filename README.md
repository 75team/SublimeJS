# Sublime JS
	
Use [Google v8 engine](http://code.google.com/p/v8/) to write plugins in JavaScript

## Writing plugin in JavaScript:

```javascript
/** index.js **/

defineCommand("Hello", require("hello.command"));
```


```javascript
/** hello.command.js **/

module.exports = function(view, edit){
	view.insert(edit, 0, "HelloWorld");
}
```

## Examples:

[SublimeJS_Samples](https://github.com/akira-cn/SublimeJS_Samples)
