
***********************************************
Qooxdoo-specific CherryPy-based JSON RPC-server
***********************************************

Overview
========

*Python* RPC-server for a `Qooxdoo <http://qooxdoo.org>`_ application. Implemented on top of 
`Cherrypy <http://cherrypy.org>`_. Supports file upload and download. Controller code example: 

.. code-block:: python

   import cherrypy
   import qxcpjsonrpc as rpc

   class Service:
    
     @cherrypy.expose
     def index(self, *args, **kwargs):
       return rpc.JsonRpcServer().run()

Service code example:

.. code-block:: python

   import qxcpjsonrpc as rpc

   class Test(rpc.JsonRpcService):

     @rpc.public
     def add(self, x, y):
       return x + y

*Qooxdoo* code example:

.. code-block:: javascript

   var rpc = new qx.io.remote.Rpc();
   rpc.setServiceName("modulename.Test");
   rpc.setUrl("http://127.0.0.1:8080/service");
   rpc.addListener("completed", function(event)
   {
     console.log(event.getData());
   });
   rpc.callAsyncListeners(this, "add", 5, 7);


Serialization
=============

Serialization is provided by ``json`` package. However it doesn't work out-of-the-box for some 
practically important types.

No special deserialization but ``json.loads`` is performed. Additional parsing is indended to be
in user code.
  

Date
----

Dates are serialized to `UTC <http://en.wikipedia.org/wiki/Coordinated_Universal_Time>`_ 
`ISO 8601 <http://www.w3.org/TR/NOTE-datetime>`_ strings, close to what *Javascript* 
`JSON.stringify(new Date())` produces. `datetime.datetime` objects look like 
`2012-03-17T19:09:12.217000Z`, `datetime.date` like `2012-03-17T00:00:00Z`.

As far as I know, there's no reliable and cross-browser way to parse *ISO 8601* strings using *Javascript* 
`Date` object. The following code can help (usually I put it to `Date.fromISOString`, as a counterpart to
`Date.prototype.toISOString`), which converts *ISO 8601* to cross-browser representation 
`2011/10/09 07:06:05 +0000` and passes it to `Date` constructor.

.. code-block:: javascript
  
  function fromISOString(value)
  {
    if(!value)
    {
      return null;
    }
    
    return new Date(value
      .split(".")[0]
      .split("Z")[0]
      .split("-").join("/")
      .replace("T", " ")
      + " +0000"
    );
  }
  
For dealing with *ISO 8601* strings in service user code there's a helper, which can be used as follows. 
Note that `datetime.datetime` objects it produces are timezone-aware. Timezone is *UTC*. 

.. code-block:: python
  
  import qxcpjsonrpc as rpc
  
  rpc.fromJsonDate('2012-03-17T19:09:12.217Z')

Decimal
-------

Serialized as strings.


Examples
========

For examples look in 
`test suite <http://code.google.com/p/qooxdoo-cherrypy-json-rpc/source/browse/#hg%2Fqxcpjsonrpc%2Ftest>`_. 
More examples could be found in `this <http://code.google.com/p/cherrypy-webapp-skeleton/>`_ project. 
