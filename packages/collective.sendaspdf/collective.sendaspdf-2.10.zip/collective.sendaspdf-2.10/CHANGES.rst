Changelog
=========

2.10 (2014-01-20)
-----------------

- Pass ``--encoding utf-8`` to wkhtmltopdf.  Fixes possible encoding
  error.
  [jean]


2.9 (2013-09-27)
----------------

- First try to import pisa from the newer xhtml2pdf library.
  Note that it can be hard for both libraries, including their
  dependencies, to find versions that work on Python 2.4 (Plone 3).
  Generally, wkhtmltopdf is recommended.
  [maurits]

- No longer convert everything to ascii for pisa.
  [maurits]

- Do the possible encoding to utf-8 in one spot, before calling
  a html_to_pdf transform method.
  [maurits]

- Do not use deprecated clean_string from jquery.pyproxy anymore.
  Requires jquery.pyproxy 0.3 or higher.
  [maurits]

- When no view_name is given, do not try to get the immediate view,
  but just display the context.  This will let the standard Zope and
  Plone machinery do its work.  Do the same when traversing to 'view'
  does not work even though viewing this url works just fine.  That
  can happen in some cases.
  [maurits]

- Moved code to https://github.com/zestsoftware/jquery.pyproxy
  [vincent, maurits]


2.8 (2012-11-01)
----------------

- added pep8/pyflakes checks fo Travis based on collective.polls
  config. [vincent]

- pep8/pyflakes [vincent + maurits]

- Added option to allow passing the authentication cookie to
  wkhtmltopdf. This fixes some issues with images hidden inside
  non-public folder (but that the user can see in the normal
  page). [vincent]


2.7.2 (2012-10-18)
------------------

- Fix exception syntax for Python 2.4 (Plone 3). [vincent]


2.7.1 (2012-10-18)
------------------

- Fixed timeout issue. [vincent]


2.7 (2012-10-17)
----------------

- added some more random in the temporary file generation to avoid
  issue with multiple concurrent runs. [vincent]

- added a timeout on the subprocess + put stdout/err in TemporaryFile
  to avoid potential issues. [vincent]

- raised number of zserver-threads in default buildout, that prevents
  the server locking. [vincent]

- Added bootstrap/buildout based on collective/tutorial.todoapp
  (https://github.com/collective/tutorial.todoapp). [vincent]


2.6 (2012-06-15)
----------------

- Updated Dutch translations. [Thom van Ledden]

- fix generating local urls with anchors [Davide Moro]

- Bugfix in update_relative_urls [Davide Moro]

2.5 (2012-03-29)
----------------

- Fixed generating pdf name [kroman0]

- Added possibility to add an adapter that will generate default
  options for PDF generation.
  Adapter must implement ISendAsPDFOptionsMaker. [vincent]

- Added layout options when generating files with wkhtmlaspdf. Options
  available are: use book style, generate table of contents, margins.
  Those options can be overriden in download links. [vincent]

- Added utility to replace relative URL and include images as data in
  the img tag. [vincent]

- Enabled possibility to render table of contents and book style using
  GET arguments. [vincent]

- Added Italian translation [giacomos]


2.4.2 (2011-12-09)
------------------

- Bugfix is JS bindings to download the PDF, it now uses the correct
  context. [vincent]

- Bugfix when the context title contains non-ascii characters. Zope
  does not accept those characters in set_header [vincent+Vladislav]


2.4.1 (2011-12-07)
------------------

- Bugfix in TinyMCE loading with Plone 4. [vincent]

- Bugfix when checking if the attachment name should be providen,
  'self.excluded_browser_attachment' does not seem to work on every
  instances, used 'self.getExcluded_browser_attachment()'
  instead. [vincent]

- Fixed test runners for Plone 4. [vincent]


2.4 (2011-11-22)
----------------

- Added a setting in send as PDF tool so we can exclude some browser
  when forcing file name. This will mainly usefull for Chrome, as this
  one considers PDF generated with the tool as potentially harmful
  files.
  The same problem will certainly appear with Chromium. [vincent]

- Display a file name based on the context's title when downloading
  the page. [Giacomo Spettoli]

- Added some functional tests. [vincent]

- Don't repeat POST parameters anymore. [vincent]


2.3.1 (2011-06-27)
------------------

- Bugfix with Unicode (again) and Ajax. [vincent]


2.3 (2011-05-25)
----------------

- Bugfix when not using secure mail host. [Yuri]

- Bugfix with wk transforms for encoding. [Khairil Yusof]


2.2 (2011-04-05)
----------------

- Fixed encoding to avoid being limitated to ASCII. [mauriziolupo]

- Added a generic setup handler for sendaspdftool and import/export
  preferences. [mauriziolupo]


2.1.1 (2010-12-23)
------------------

- added a target (sic :/) attributes on the link to preview the PDF so
  it opens in a new window. That's prety ugly, but the fact is that if
  a user clicks on the link with IE and Acrobat reader installed, it
  will open the PDF in the same window. Hitting the 'back' button will
  display the page without the Ajax form. [vincent]

- in the Ajax popup, we do not try to initialize tinymce is an error
  happenned. [vincent]

- another IE bugfix due to an extra comma + CSS opacity fix [vincent]


2.1 (2010-12-15)
----------------

- also added meta tag robots:noindex on the forms. [vincent]

- Added header 'X-Robots-Tag': 'noindex' in downloaded file to avoid
  having it indexed by search engines. [vincent]

- Bugfix when sumbitting the Ajax form with TinyMCE. [vincent]


2.0.1 (2010-11-11)
------------------

- Bugfix in jquery.sendaspdf.js - removed one comma that was causing
  an error in IE. [vincent]


2.0 (2010-10-22)
----------------

- compatibility fixes with Plone4. [vincent]

- added Ajax version of "Download as PDF" link. [vincent]

- added Ajax version of the "Send as PDF" link. [vincent]

- Removed the '-C' parameter. [yuri + vincent]


1.1 (2010-09-16)
----------------

- when the PDF generation failed in the page to send by mail, we
  display an error page instead of failing. [vincent]

- bugfix in send page - it was impossible to load the Wysiwyg for
  anonymous users. Stole some code from POI to solve it. [vincent]


1.0.3 (2010-08-02)
------------------

- Fix broken release with missing files. (Now released with setuptools-git
  installed.) [mark]


1.0.2 (2010-08-02)
------------------

- updated egg information in setup.py (author and description). [mark]


1.0.1 (2010-08-02)
------------------

- translated the "download as PDF" action. [mark]

- registered the translations so they are applied. [mark]


1.0 (2010-07-21)
----------------

- added Dutch and French translations [vincent+mark]

- added view to send by mail and download the page. [vincent]

- added document actions to send the page by mail and download as
  pdf. [vincent]

- Added sendaspdf tool to manage preferences. [vincent]
