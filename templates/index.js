Dropzone.autoDiscover = false;

if (!window.chrome) {
    alert("Unsupported browser. Only Chrome on Desktop is supported.");
}

var randomString = function() {
    var text = "";
    var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    for (var i = 0; i < 5; i++)
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    return text;
};

$(function () {
    var data = [];

    var container = document.getElementById('handsontable');
    hot = new Handsontable(container, {
        data: data,
        rowHeaders: true,
        colHeaders: true,
        wordWrap: false,
        manualColumnResize: true,
        stretchH: 'all',
        autoColumnSize: true,
        contextMenu: true

    });

    var dropzone = new Dropzone(document.body, {url: "/upload"});
    dropzone.on("drop", function (args) {
        $("#loader").show();
    });
    dropzone.on("error", function (args) {
        alert("An error occurred. See JavaScript console for details.");
    });
    dropzone.on("success", function (args) {
        $("#loader").hide();
        root = JSON.parse(args.xhr.response);
        hot.loadData(root.table_data);

        // random string for cache-busting
        PDFObject.embed(root.searchable_pdf_url + "?" + randomString(), "#pdf-div", {
            pdfOpenParams: {
                toolbar: '0',
                page: '1',
                view: 'FitBV'
            }
        });

        $("#handsontable").css("display", "inherit");
        $("#help").hide();

        $("#source-name-root").show();
        $("#source-name").text(args.name);

        var resizeTable = function() {
            var navbarH = $("nav").height();
            var bodyH = $("body").height();
            $(".mytd").height(bodyH - navbarH);
            $("#pdf-div").height(bodyH - navbarH);

            hot.updateSettings({
                "width": $(hot.rootElement).parent().width(),
                "height": $(hot.rootElement).parent().height()
            });
            hot.render();
        };

        resizeTable();

        var resizeWindow = function() {
            resizeTable();
        };

        var timeout;
        $(window).resize(function () {
            clearTimeout(timeout);
            timeout = setTimeout(resizeWindow, 100);
        });

        var onSampleResized = function(e) {
            var table = $(e.currentTarget);
            resizeTable();
        };

        $(".mytable").colResizable({
            liveDrag: true,
            onResize: onSampleResized
        });
    });

    var exportPlugin = hot.getPlugin('exportFile');
    $("#export-csv").click(function () {
        exportPlugin.downloadFile('csv', {filename: 'data'});
    });
});