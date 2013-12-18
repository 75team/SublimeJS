# Sublime JS
	
Use [Google v8 engine](http://code.google.com/p/v8/) to write plugins in JavaScript

## Writing plugin in JavaScript:

* add a package.json file:

```json
{
  "name": "JSDemo",
  "description": "demo plugin powered by SublimeJS",
  "version": "0.1.0",
  "author": {
    "name": "akira-cn",
    "email": "akira.cn@gmail.com"
  },
  "main": "index.js",
  "licenses": [
    {
      "type": "The MIT License",
      "url": "http://www.opensource.org/licenses/mit-license.php"
    }
  ]
}
```

* add Javascript files:

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

## Thanks

Thanks to [emmet-sublime](https://github.com/sergeche/emmet-sublime).
Some idea is borrowed from emmet-sublime. :-)
