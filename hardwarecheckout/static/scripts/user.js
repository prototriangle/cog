$(document).ready(function() {
    $('.update-user').api({
        action: 'update user',
        method: 'POST',
        serializeForm: true,
        onFailure: function(data) {
            var $form = $(this).closest('form');
            var $error = $form.find('.message').first();
            $error.html(data.message);
            $error.show();

            if(data.user) {
                $('input[name="name"]', $form).val(data.user.name);
                $('input[name="phone"]', $form).val(data.user.phone);
                $('input[name="location"]', $form).val(data.user.location);
            }
        },
    })
    .state({
        onActivate: function() {
          $(this).state('flash text');
        },
        text: {
          flash: 'Info updated!'
        }
    });
    $(':file').on('change', function() {
        var file = this.files[0];
        if (file.size > 10 * 1024 * 1024) {
            alert('max upload size is 10MB');
            this.value = "";
        }
    });

    $(':button').on('click', function() {
        var $error = $('form').find('.message').first();
        $error.hide();
        if ($('#cvupload').get(0).files.length < 1) {
            return;
        }
        if ($('#cvupload').get(0).files[0].size > 10 * 1024 * 1024) {
            $('.error.message').html('File too large!');
            $('.error.message').show();
            return;
        }
        $('#sponsor-agreement').modal('show');
        $('#sponsor-agreement').modal({
            onApprove: onDataAgree
        });
    });

    function onDataAgree() {
        $.ajax({
            url: 'cvupload',
            type: 'POST',

            data: new FormData($('form')[0]),

            cache: false,
            contentType: false,
            processData:false,

            complete: function(jqXHR, textStatus) {
                response = JSON.parse(jqXHR.responseText);
                if (!response['success']) {
                    $('.error.message').html(response['reason']);
                    $('.error.message').show();
                } else {
                    $('#cvlabel')[0].innerHTML = "CV Uploaded";
                    $modalcontent = $('#sponsormodalcontent');
                    if ($modalcontent.children().length < 2) {
                        $('<p>', {
                            text: "You have already uploaded a CV, are you sure you want to replace it?"
                        }).appendTo($modalcontent);
                    }
                }
            },

            xhr: function() {
                var myXhr = $.ajaxSettings.xhr();
                if (myXhr.upload) {
                    myXhr.upload.addEventListener('progress', function(e) {
                        if (e.lengthComputable) {
                            console.log(e.loaded + '/' + e.total);
                        }
                    }, false);
                }
                return myXhr;
            }
        });
    }

    // enables items_list actions
    $('.item-action').api({
        method: 'POST',
        onSuccess: function (data) {
            $error = 
               $(this).closest('form').find('.message').first();
            $error.hide();
    
            if (data.return_id) 
                $('.return-notice').modal('show');
            else 
                setTimeout(function() {
                    window.location.reload();
                }, 250); 
        },
        onFailure: function(data) {
            $error = $('.message').filterByData('table-id', 
                $(this).data('table-id')).first();
            console.log($error);
            $error.html(data.message);
            $error.show();
        }
    });

    $('.request-action').api({
        method: 'POST',
        onSuccess: function(response) {
            window.location.reload();
        },
        onFailure: function(err) {
            console.log(err);
            alert(err.message)
        }
    });
});
