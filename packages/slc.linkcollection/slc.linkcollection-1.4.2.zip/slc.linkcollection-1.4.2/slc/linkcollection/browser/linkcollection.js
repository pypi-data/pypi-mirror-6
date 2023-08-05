/* Old style link collection, using referenced documents and a viewlet */

var LinkCollection = { };
// Height of the tallest document which has been displayed
LinkCollection.maxheight = 0;
LinkCollection.render_doc = function render_doc(node, uid) {
    jq('a.current-linklist-item').removeClass('current-linklist-item');
    jq(node).addClass('current-linklist-item');
    jq('li.current').removeClass('current');
    jq(node.parentNode).addClass('current');

    jq('div.prefetched-docs').each(
    function(i){
        if (jq(this).is(':visible')) {
        jq(this).hide();
        }
    }
    );

    var doc = jq('div#doc-'+uid);
    doc.fadeIn(300);

    /* Prevent the page from jumping up and down for long and short
    documents by setting the height of the current doc to the
    height of the largest doc displayed so far. */
    /* I'm deactivating this, because I consider it harmful. If you view a long
    page, then a very short one, the footer will not be visible. Valuable links
    might not be accessible.
    Besides, the "page jumping" only seems to happen in FF, not in
    Safari, Chrome and Opera.
    Wolfgang Thomas 11.11.2010 */
    /* if (doc.height() > LinkCollection.maxheight) {
     LinkCollection.maxheight = doc.height();
    }
    doc.height(LinkCollection.maxheight); */

    // Scroll to the top of the linkbox
    var linkbox=jq('div#slc-linkcollection-linkbox');
    var linkboxtop=linkbox.offset().top;
    var body=jq('html,body');
    body.scrollTop(linkboxtop);
    return false;
}

/* New style link collection, all content in one document, usinj jQuery */
jq(function() {
    var elems = jq("h2.linkcollection");
    jq("h2.linkcollection").nextAll().andSelf().wrapAll('<div id="tabs" />');
    jq("<ul id='slc-linkcollection-list' class='navigationLinkBox'></ul>").prependTo("#tabs");
    for (var i=0;i<elems.length;i++)
    {
        var listel = jq("<li>")[0];
        var linkel = jq("<a href='#tabs-" + i + "' class='linkcollectionAnchor'></a>)")[0];
        jq(linkel).append(jq(elems[i]).text());
        jq(listel).append(linkel);
        jq("#tabs ul#slc-linkcollection-list").append(listel);
        jq(elems[i]).nextUntil("h2.linkcollection").andSelf().wrapAll("<div class='paneContent' id='tabs-" + i + "' />");
    }
    jq('#tabs div.paneContent').wrapAll("<div class='panes' />");
    jq('#tabs').before('<a name="linkcollectionNavi"></a>');
    var actual_url = jq('#actual-url').text();
    jq('#tabs').after('<span class="linkToTopAnchor"><a href="' + actual_url + '#linkcollectionNavi" class="solitaryLink linkcollectionAnchor" i18n:translate="label_go_up">Go up</a></span>');
    jq('#tabs').after('<div class="visualClear"></div>');
    jq("ul.navigationLinkBox").tabs('div.panes > div.paneContent');
});

var jump=function(e)
{
    //prevent the "normal" behaviour which would be a "hard" jump
    e.preventDefault();
    //Get the target
    var target = jq("#tabs");
    //perform animated scrolling
    jq('html,body').animate(
    {
      //get top-position of target-element and set it as scroll target
      scrollTop: jq(target).offset().top
      //scrolldelay: 2 seconds
    },500,function()
    {
     // do nothing more
    });
}

jq(document).ready(function()
{
    jq('a[href*=#].linkcollectionAnchor').bind("click", jump);
    return false;
});

