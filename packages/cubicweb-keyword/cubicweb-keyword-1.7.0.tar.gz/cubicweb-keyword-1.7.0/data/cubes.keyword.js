/*
 *  :organization: Logilab
 *  :copyright: 2003-2008 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
 *  :contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
 */

CubicWeb.require('python.js');
CubicWeb.require('ajax.js');
CubicWeb.require('widgets.js');

var kwform = null;

/* callback called when tag-edition is finished */
function validateKeywords(kwform, kwlist) {
    var eid = kwform.eid;
    d = asyncRemoteExec('add_keywords', eid, kwlist);
    d.addCallback(function(msg) {
	log('got message', msg);
 	reloadComponent('keywordsbar', 'Any X WHERE X eid '+eid, 'contentnavigation');
  	document.location.hash = '#header';
 	kwform.destroy();
 	updateMessage(msg);
    });
}


function onkwformDestroy() { kwform = null;}

/* builds the tagselection widget */
function showKeywordSelector(eid, oklabel, cancellabel) {
    // if tagform is already on screen, destroy it
    if (kwform) { kwform.destroy(); }
    else {
	kwform = new Widgets.SuggestForm('kwinput', 'possible_keywords', [eid],
					  validateKeywords, {multi : true,
							     oklabel : oklabel,
							     cancellabel : cancellabel});
	kwform.eid = eid // gruik !
	connect(kwform, 'destroy', onkwformDestroy);
	kwform.show($('kwformholder'));
    }
}

Cubicweb.provide('keywords.js');
