What
====

isk-daemon is an open source database server capable of adding content-based (visual) image searching to any image related website or software.

We‘re looking for ways to improve the adoption of such technology. Please let us know if you can benefit from it and need some help getting it to work for you.

This technology allows users of any image-related website or software to sketch on a widget which image they want to find and have the website reply to them the most similar images or simply request for more similar photos at each image detail page.

Key features:

* Query for images similar to one already indexed by the database, returning a similarity degree for the images on database that most resemble the target query image;
* Query for images similar to one described by its signature. A client-side widget may generate such signature from what a user sketched and submit it to the daemon;
* Network interface for easy integration with other web or desktop applications: XML-RPC, SOAP;
* Fast indexing of images one-by-one or in batch;
* Associate keywords to images and perform image-similarity queries filtering by keywords;
* Quickly remove images from database one-by-one or in batch;
* Built-in web-based admin interface with statistics and ad-hoc maintenance commands/API testing;
* Optimized image processing code (implemented in C++).

Install instructions
====================

Installation, usage instructions and more details are available online at http://www.imgseek.net/isk-daemon/documents-1/install-and-usage

Latest source code
==================

See github: https://github.com/ricardocabral/iskdaemon/

Credits
==========

imgSeek and isk-daemon portions copyright Ricardo Niederberger Cabral (ricardo.cabral at imgseek.net).

Image loading code is credited to "ImageMagick Studio LLC" and library linkage adheres to statements on ImageMagick-License.txt

Support or Donate
====================

Help on improving this software is needed, feel free to submit patches.
