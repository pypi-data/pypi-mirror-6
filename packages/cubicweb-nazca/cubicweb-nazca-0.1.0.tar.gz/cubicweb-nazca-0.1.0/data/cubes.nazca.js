cw.cubes.nazca = new Namespace('cw.cubes.nazca');
cw.cubes.nazca.counter = 0;
cw.cubes.nazca.language = 'en';
cw.cubes.nazca.translations = {'fr': {'see_results': 'Voir les résutats sous forme : ',
                                'choose_option':'Veuillez choisir une option.',
                                'done':'Effectué','aborded':'Arrêté avec erreurs',
                                 'align_wait':'Alignement en cours, veuillez patienter...'},
                               'en': {'see_results':'See the results in: ',
                                 'choose_option':'Please, choose an option.',
                                 'done':'Done', 'aborded':'Aborted',
                                 'align_wait':'Please wait while aligning...'}
                               };

$.extend(cw.cubes.nazca, {
  removeOption: function($this, dataName){
    $('[data-'+dataName+'=' + $this.attr('data-'+dataName) + ']').remove();
  },

  i18n: function(msg){
     return cw.cubes.nazca.translations[cw.cubes.nazca.language][msg];
  },
  setLanguage: function(lng){
     cw.cubes.nazca.language = lng;
   },

  addNewOption: function($this, dataName, holderId){
        var value = $this.siblings('select').val();
        if (value.length > 0) {
            cw.cubes.nazca.counter += 1;
            var idx = cw.cubes.nazca.counter;
            $("#alert").addClass('hidden');
            var d = asyncRemoteExec('load_'+dataName+'_options', value, idx);
            d.addCallback(function(options) {
               $('#'+holderId).append('<li class="form-group" data-'+dataName+'="'+idx+'">'+ options + '</li>');
               $('a[rel=popover]').popover({'html':true});
            });
        } else {
           $("#alert div #msg").html(cw.cubes.i18n('see_results'));
           $("#alert").removeClass('hidden');
        }
    },

    typeChange:function(set){
        var filetype = $('#__'+set+'type').val();
        if (filetype == 'csv') {
            $('.group-'+set+'query').fadeOut('slow', function() {
                $('#group-'+set+'file').fadeIn('slow');
                                             });
        } else {
            $('#group-'+set+'file').fadeOut('slow', function() {
                $('.group-'+set+'query').fadeIn('slow');
                                          });
        }
    },

    checkProgress:function(divid){
        var d = asyncRemoteExec('checkprogress');
        d.addCallback(function(results) {
            if (results.msg !== null) {
                $(divid).append('<li>' + results.msg + '</li>');
            }
            if (results.finished === true) {
                var a = asyncRemoteExec('get_outputs');
                a.addCallback(function(outputs) {
                    var links = [];
                    for (var i = 0 ; i < outputs.length; i++) {
                        links.push('<a href="' + BASE_URL + '?vid=nazca-'
				   + outputs[i] + '-results" target="_blank">' + outputs[i] + '</a>');
                    }
                    $(divid).append('<li>' + cw.cubes.nazca.i18n('see_results') + links.join(', ') + '</li>');
                    updateMessage(cw.cubes.i18n('done'));
                });
            }
            else if (results.error !== true) {
                setTimeout(function() { cw.cubes.nazca.checkProgress(divid); },
                    2000);
            }
            else { updateMessage(cw.cubes.nazca.i18n('aborded')); }
        });
        updateMessage(cw.cubes.nazca.i18n('align_wait'));
    }

});
