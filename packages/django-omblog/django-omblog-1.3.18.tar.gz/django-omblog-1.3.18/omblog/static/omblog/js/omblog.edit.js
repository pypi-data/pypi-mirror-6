/*global $,ich,window,Mousetrap,FormData,XMLHttpRequest,document */
"use strict";


$(function () {
    /* setup templates */
    ich.grabTemplates();

    /* populate span.blog_url */
    $('span.blog_url').text(window.omblog_url);

    /* slugify the input */
    $('#id_slug').slugify('#id_title');

    /* the thumbails */
    function hide_all() {
        $('div.panel').each(function () {
            $(this)
                .css('left', '-1000px')
                .addClass('hidden');
            $('div.write').removeClass('inactive');
        });
    }

    /* handle changes to the links when the slug is saved */
    function update_slug(data) {
        var el = $('a.view');
        el.attr('href', el.data('base-url') + data.slug);
        el.attr('data-slug', data.slug);
    }

    function process_invalid(data) {
        /* feedback */
        $('.feedback p').addClass('error');
        $('.feedback span.msg').text('Oh noes, errors.');
        $('.feedback span.icon').removeClass('rotate').html('&#x25;');
        setTimeout(function () {
            $('.feedback').fadeOut(200);
        }, 2000);

        /* process the errors for settings */
        if (data.errors.slug) {
            $('form #id_slug')
                .parent()
                .addClass('errors');
        }

        /* process the errors for settings */
        if (data.errors.title) {
            $('form #id_title')
                .parent()
                .addClass('errors');
        }
    }

    function process_valid(data) {
        $('.feedback p').addClass('success');
        $('.feedback span.msg').text('Post has been saved');
        $('.feedback span.icon').removeClass('rotate').html('&#x23;');
        update_slug(data);
        setTimeout(function () {
            $('.feedback').fadeOut(200);
        }, 1000);
    }

    /* presend clean */
    function presend_clean() {
        /* clean forms */
        $('form fieldset').removeClass('errors');

        /* clean feedback */
        $('.feedback p').attr('class', '');
        $('.feedback span.icon').show();
        $('.feedback').show();
    }

    /* save */
    function save() {
        /* do icons */
        $('div.feedback span.msg')
            .text('Saving');
        $('div.feedback span.icon')
            .addClass('rotate')
            .html('&#x26;');

        /* send ajax */
        $.ajax({
            type: 'POST',
            url: window.location.href,
            data: $('form').serialize(),
            ajaxSend: presend_clean(),
            success: function (data, textStatus, jqXHR) {
                if (data.success === false) {
                    process_invalid(data, textStatus, jqXHR);
                } else {
                    process_valid(data, textStatus, jqXHR);
                }
            },
            error: function (errorThrown) {
                console.log(errorThrown);
            }
        });
    }

    /* handle tabs */
    $('#id_source_content').keydown(function (e) {
        if (e.keyCode === 9) { // 9 is tab
            var start = this.selectionStart,
                end = this.selectionEnd,
                $this = $(this);
            $this.val($this.val().substring(0, start)
                        + "\t"
                        + $this.val().substring(end));
            this.selectionStart = this.selectionEnd = start + 1;

            /* prevent the focus loss */
            return false;
        }
    });

    /* add mouse trap to all inputs and text areas */
    $('input, textarea, select').addClass('mousetrap');

    /* ctrl+s saves */
    Mousetrap.bind(['ctrl+s', 'meta+s'], function (e) {
        if (e.preventDefault) {
            e.preventDefault();
        } else {
            e.returnValue = false;
        }
        save();
    });

    /* esc hides all */
    Mousetrap.bind(['esc', 'escape'], hide_all);

    /* handle upload progress */
    function updateProgress(e) {
        var position    =  e.loaded,
            total       = e.total,
            completed   = (position / total) * 100;
        $('div.completed').width(completed + '%');
    }

    /* now the drag and drop */
    function handleDragOver(e) {
        e.stopPropagation();
        e.preventDefault();
        return false;
    }

    /* load response from server */
    /*jslint unparam: true*/
    function load(e, t) {
        var i       = 0,
            data    = null,
            img     = null,
            thumb   = '';

        /* hide the progress bar after ones second. */
        $('div.progress').fadeOut(500, function () {
            $('div.completed').width('0');
        });

        /* parse the response as json */
        if (this.status === 200) {
            data  = JSON.parse(this.response);
            for (i; i < data.attachments.length; i += 1) {
                img = data.attachments[i];
                thumb   = ich.postimage({
                    title: img.title,
                    thumb: img.thumb,
                    large: img.large,
                    pk: img.pk
                });
                $('#images').append(thumb);

                /* now attach the event listeners */
                thumb[0].addEventListener('dragstart', deleteImageDragStart, false);
                thumb[0].addEventListener('dragend', deleteImageDragEnd, false);
            }
        }
    }

    /* handle drop for the images */
    function handleDrop(e) {
        e.stopPropagation();
        e.preventDefault();

        var files       = e.dataTransfer.files,
            formData    = new FormData(),
            req         = new XMLHttpRequest(),
            i = 0;

        formData.append('post', $('body').attr('data-post-pk'));

        for (i; i < files.length; i += 1) {
            formData.append(files[i].name, files[i]);
        }

        // hook up the listeners
        req.upload.addEventListener('progress', updateProgress, false);
        req.addEventListener('load', load, false);

        // show the progress
        $('div.progress').show();

        // open and send
        req.open('POST', window.attach_create_url, true);
        req.send(formData);

        // hook up the progress
        return false;
    }

    /* hand dragstart for images */
    function deleteImageDragStart(e) {
        /* set the feedback */
        $('#dropbox .instructions')
            .addClass('delete')
            .text('Drag images into this box to delete');

        /* remove the upload event listener */
        document.getElementById('dropbox-target').removeEventListener('drop', handleDrop, false);

        /* add the new delete image event listener */
        document.getElementById('dropbox-target').addEventListener('drop', deleteImageDrop, false);
    }

    /* handle dragend for images */
    function deleteImageDragEnd(e) {
        /* set the feedback */
        $('#dropbox .instructions')
            .removeClass('delete')
            .text('Drag images into this box to upload');

        /* add the upload event listener */
        document.getElementById('dropbox-target').addEventListener('drop', handleDrop, false);
    }

    /* delete image drag events */
    function deleteImageDrop(e) {
        var pk       = e.dataTransfer.getData('pk'),
            markdown = e.dataTransfer.getData('text/plain'),
            original_text = $('#id_source_content').val(),
            new_text = '';

        /* now remove the Image event listeners */
        document.getElementById('dropbox-target').removeEventListener('drop', deleteImageDrop, false);

        /* replace with the originals */
        document.getElementById('dropbox-target').addEventListener('drop', handleDrop, false);

        $.ajax({
            type: 'POST',
            url: window.attach_delete_url,
            data: {pk: pk},
            success: function () {
                /* remove from the dom */
                $('.postimage[data-pk=' + pk + ']')
                    .fadeOut(200, function () {
                        $(this).remove();
                    });

                /* remove any references to the image from textarea */
                new_text = original_text.replace(markdown, '');
                $('#id_source_content').val(new_text);

            },
            error: function (jqXHR, textStatus, errorThrown) {
                console.log(jqXHR);
                console.log(textStatus);
                console.log(errorThrown);
            }
        });
        e.preventDefault();
    }

    /* attach the listeners to all images */
    var images  = document.getElementsByClassName('postimage'),
        i       = 0;
    for (i; i < images.length; i += 1) {
        images[i].addEventListener('dragstart', deleteImageDragStart, false);
        images[i].addEventListener('dragend', deleteImageDragEnd, false);
    }

    /* attach to the upload listeners */
    document.getElementById('dropbox-target').addEventListener('dragover', handleDragOver, false);
    document.getElementById('dropbox-target').addEventListener('drop', handleDrop, false);
});
