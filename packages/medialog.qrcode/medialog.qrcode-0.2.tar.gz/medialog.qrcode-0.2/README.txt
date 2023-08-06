
Usecases
--------

- You probably only need this product if you deal with printed material (adds, reports, business cards etc).
- The main purpose for this product is to have an easy way of linking to web content from printed material.
- Lets say you are producing "printed data sheets" of products managed in Plone, but want the possibility to let readers "read more", or see the latest price. You can then include the qrcode.
- Lets say you have a (psychical) shop where you want the price tags to include "info about the product".
- Let say you are producing product labels and you want them to include a link to "how to use this product", where to re-order etc.
- Hide the qrcode with CSS and show it in print.css (or add it to the pdf template)


Viewlet
----------
There is also a related viewlet.
The main purpose for this will when printing the page.
You can enable the viewlet by adding medialog.qrcode.interfaces.IqrcodeLayer to your content.


Behaviour
----------
There is also a dexterity behavior.


Browser view
------------
This product adds a browser view that generates a QRcode for the given page.
It also adds a portlet that will show a QR code. 
The portlet has an option for hiding it for anon users.


Use the browser view like this:

http://mysite.com/mypage/@@qrcode
To get a qrcode for http://mysite.com/mypage 

Or:
http://mysite.com/mypage/@@qrimage?view=myview
To get a qrcode for http://mysite.com/mypage/myview

Or:
http://mysite.com/@@qrimage?url=http://somewhere.com/somepage
To get a qrcode for url=http://somewhere.com/somepage



Note:
-----
If the browser view is used on an ATlink object with external link, you will get the QR-code for that URL.