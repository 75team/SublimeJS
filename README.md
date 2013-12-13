# sublime-v8
	
 added [Google v8 engine](http://code.google.com/p/v8/) to sublime text 2

## Realtime syntax checking with [PyV8](https://github.com/okoye/PyV8)

 check & mark syntax errors

## Show [jshint](http://www.jshint.com/) result by press ctrl+alt+h key
	
 jshint result can be shown (including errors and warnings)
 
 with jshint settings in JSHINT.sublime-settings 

## A JavaScript console supported

 a js console shown by press ctrl+alt+j key
 
 use it like the python console

## Writing plugin in JavaScript:
	
     //example
     require('base');

     exports = TextCommand("HelloWorld", function(view, edit){
         view.insert(edit, 0, "HelloWorld");
         console.log(view.file_name());
     });

## Troubeshooting

 If the plugin doesn't work, follow the guide - lib/PyV8/README.md.