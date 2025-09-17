export default{
    truncate(text, { length = 30, omission = '...', separator } = {}) {
        if (text == null) return '';
        const str = String(text);
        if (str.length <= length) return str;
        const end = length - omission.length;
        if (end < 1) return omission;
        let slice = str.slice(0, end);
        if (separator) {
            const sepIdx = slice.lastIndexOf(separator);
            if (sepIdx > -1) {
                slice = slice.slice(0, sepIdx);
            }
        }
        return slice + omission;
    },
    escapeAttr(value) {
        // Normalize first so objects/arrays become readable JSON not [object Object]
        let str;
        if (value == null) {
            str = '';
        } else if (typeof value === 'string') {
            str = value;
        } else if (typeof value === 'number' || typeof value === 'boolean') {
            str = String(value);
        } else {
            try {
                str = JSON.stringify(value);
            } catch {
                str = String(value);
            }
        }
        return str
            .replace(/&/g, '&amp;')
            .replace(/"/g, '&quot;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
    },
    is_local: function(){
        if(location.host === 'localhost:8071'){
            return true
        }
        return false
    },
  apiError: function ( resp ) {
    var error_str = '';
    if ( resp.status === 400 ) {
      try {
        let obj = JSON.parse( resp.responseText );
        error_str = obj.non_field_errors[ 0 ].replace( /[[\]"]/g, '' );
      }
      catch ( e ) {
        console.log(e);
        error_str = resp.responseText.replace( /[[\]"]/g, '' );
      }
    }
    else if ( resp.status === 404 ) {
      error_str = 'The resource you are looking for does not exist.';
    }
    else {
      error_str = resp.responseText.replace( /[[\]"]/g, '' );
    }
    return error_str;
  },
    apiVueResourceError: function(resp){
        var error_str = '';
        var text = null;
        console.error(JSON.stringify(resp));
        try {
          if (resp.status === 400) {
              if (Array.isArray(resp.body)){
                  text = resp.body[0];
              }
              else{
                  text = resp.body;
              }
 
              if (typeof text == 'object'){
                  if (Object.prototype.hasOwnProperty.call(text, 'non_field_errors')) {
                      error_str = text.non_field_errors[0].replace(/[[\]"]/g, '');
                  }
		  else if (Array.isArray(text) && 'errors' in text) {
	              error_str = text.errors
	          }
    	          else if ('errors' in text) {
	              error_str = text.errors
	          }
                  else {
                      error_str = text;
                  }
              }
              else{
                  error_str = text.replace(/[[\]"]/g,'');
                  error_str = text.replace(/^['"](.*)['"]$/, '$1');
              }
          }
          else if ( resp.status === 404) {
              error_str = 'The resource you are looking for does not exist.';
          }
          else {
              try {
                  error_str = JSON.stringify(resp.data.errors).substring(0, 400);
              } catch (error) {
                  console.log(error)
                  error_str = JSON.stringify(resp).substring(0, 400);
              }
	  }
        }
        catch ( e ) {
          console.log(e)
          error_str = JSON.stringify(resp).substring(0, 400);
        }
        return (typeof text == 'object') ? JSON.stringify(error_str) : error_str
    },

  goBack: function ( vm ) {
    vm.$router.go( window.history.back() );
  },
  copyObject: function(obj){
        return JSON.parse(JSON.stringify(obj));
  },
  getCookie: function ( name ) {
    var value = null;
    if ( document.cookie && document.cookie !== '' ) {
      var cookies = document.cookie.split( ';' );
      for ( var i = 0; i < cookies.length; i++ ) {
        var cookie = cookies[ i ].trim();
        if ( cookie.substring( 0, name.length + 1 )
          .trim() === ( name + '=' ) ) {
          value = decodeURIComponent( cookie.substring( name.length + 1 ) );
          break;
        }
      }
    }
    return value;
  },
  namePopover: function ( $, vmDataTable ) {
    vmDataTable.on( 'mouseover', '.name_popover', function () {
      $( this )
        .popover( 'show' );
      $( this )
        .on( 'mouseout', function () {
          $( this )
            .popover( 'hide' );
        } );
    } );
  },
  add_endpoint_join: function ( api_string, addition ) {
    // assumes api_string has trailing forward slash "/" character required for POST
    return api_string + addition;
  },
  add_endpoint_json: function ( string, addition ) {
    var res = string.split( ".json" )
    return res[ 0 ] + '/' + addition + '.json';
  },
  dtPopover(value, truncate_length = 30, trigger = 'hover') {
        const ellipsis = '...';
        const raw = value == null ? '' : String(value);
        const truncated = this.truncate(raw, {
            length: truncate_length,
            omission: ellipsis,
            separator: ' ',
        });
        let result = '<span>' + truncated + '</span>';
        if (raw.length > truncated.length) {
            result += `<a class="mx-0 ps-1 pe-0" href="javascript://"
                role="button"
                data-bs-toggle="popover"
                data-bs-trigger="${this.escapeAttr(trigger)}"
                data-bs-placement="top"
                data-bs-html="true"
                data-bs-content="${this.escapeAttr(raw)}"
            ><small>More</small></a>`;
        }
        return result;
    },
    dtPopoverCellFn: function(){
        // $(cell).find('[data-bs-toggle="popover"]')
        //     .popover()
        //     .on('click', function (e) {
        //         e.preventDefault();
        //         return true;
        //     });
        
        let popoverTriggerList = [].slice.call(
            document.querySelectorAll('[data-bs-toggle="popover"]')
        );
        // eslint-disable-next-line no-unused-vars
        let popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    },
    enablePopovers: function () {
        let popoverTriggerList = [].slice.call(
            document.querySelectorAll('[data-bs-toggle="popover"]')
        );
        // eslint-disable-next-line no-unused-vars
        let popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    },
    guid: function(){
      function s4(){
        return Math.floor((1 + Math.random()) * 0x10000).toString(16).substring(1);
      }
      return s4() + s4() + '-' + s4() + '-' + s4() + '-' + s4() + '-' + s4() + s4() + s4();
    },
    mimic_redirect: function(url, postData){
        console.log('in mimic...')
        /* http.post and ajax do not allow redirect from Django View (post method),
           this function allows redirect by mimicking a form submit.

           usage:  vm.post_and_redirect(vm.application_fee_url, {'csrfmiddlewaretoken' : vm.csrf_token});
        */
        var postFormStr = "<form method='POST' action='" + url + "'>";

        for (var key in postData) {
            if (Object.prototype.hasOwnProperty.call(postData, key)) {
                postFormStr += "<input type='hidden' name='" + key + "' value='" + postData[key] + "'>";
            }
        }
        postFormStr += "</form>";
        var formElement = $(postFormStr);
        $('body').append(formElement);
        $(formElement).submit();
    },
    processError: async function(err){
        console.log(err)
        let errorText = '';
        if (err.body.non_field_errors) {
            console.log('non_field_errors')
            // When non field errors raised
            for (let i=0; i<err.body.non_field_errors.length; i++){
                errorText += err.body.non_field_errors[i] + '<br />';
            }
        } else if(Array.isArray(err.body)) {
            console.log('isArray')
            // When serializers.ValidationError raised
            for (let i=0; i<err.body.length; i++){
                errorText += err.body[i] + '<br />';
            }
        } else {
            console.log('else')
            // When field errors raised
            for (let field_name in err.body){
                if (Object.prototype.hasOwnProperty.call(err.body, field_name)){
                    errorText += field_name + ':<br />';
                    for (let j=0; j<err.body[field_name].length; j++){
                        errorText += err.body[field_name][j] + '<br />';
                    }
                }
            }
        }
        await swal.fire({
            title: "Error",
            text: errorText,
            icon: "error"
        });
    },
};
