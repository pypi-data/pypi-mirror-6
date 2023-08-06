
cw.cubes.brainomics = new Namespace('cw.cubes.brainomics');

$.extend(cw.cubes.brainomics, {
    getCurrentRql: function(){
	// XXX This should be done in a more easier way...
	var divid = 'pageContent';
	var vidargs = '';
	// Get facet rql
	//jQuery(CubicWeb).trigger('facets-content-loading', [divid, '', '', vidargs]);
	var $form = $('#' + divid + 'Form');
	if ($form.length != 0){
	    var zipped = facetFormContent($form);
	    zipped[0].push('facetargs');
	    zipped[1].push(vidargs);
	    return zipped;}
	else{return null;}
    },

    seeRelatedData: function(datatype, current_etype) {
	var zipped = cw.cubes.brainomics.getCurrentRql();
	if (zipped != null){
	    var d = loadRemote(AJAX_BASE_URL, ajaxFuncArgs('filter_build_rql', null, zipped[0], zipped[1]));
	    d.addCallback(function(result) {
		    var rql = result[0];
		    var dd = asyncRemoteExec('see_related_data', rql, datatype, current_etype);
		    dd.addCallback(function(res) {window.location = res;});
		    });
	    };
    },

    changeDownloadUrls: function(){
	/* Change the download urls for facet rql */
	var zipped = cw.cubes.brainomics.getCurrentRql();
	var d = loadRemote(AJAX_BASE_URL, ajaxFuncArgs('filter_build_rql', null, zipped[0], zipped[1]));
	d.addCallback(function(result) {
		    var rql = result[0];
		    $.each($('.download-ctx'), function(index, value){
			    this.href = BASE_URL+'?rql='+rql+'&vid='+this.id;
			    console.log(BASE_URL+'?rql='+rql+'&vid='+this.id);});
		    });
	}
});