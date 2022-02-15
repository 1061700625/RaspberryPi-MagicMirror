;(function ($, document, window) {
    $.pictureViewer = function (options) {
        var pictureViewer_html =    '<div id="pictureViewer">' +
                                    '<div class="content">' +
                                    '<div class="menu-bar">' +
                                    '<div class="handel close-view" title="\u5173\u95ED(ESC)"></div>' +
                                    '<div class="handel maximization" title="\u6700\u5927\u5316"></div>' +
                                    '<div class="handel miniaturization hide" title="\u5C0F\u7A97\u53E3"></div>' +
                                    '<div class="clear-flex"></div>' +
                                    '</div>' +
                                    '<div class="handel-prev left" title="\u4E0A\u4E00\u5F20(\u2190)"></div>' +
                                    '<div class="picture-content">' +
                                    '<img class="cover" src="">' +
                                    '</div>' +
                                    '<div class="handel-next right" title="\u4E0B\u4E00\u5F20(\u2192)"></div>' +
                                    '<div class="counter">' +
                                    '<span class="num"></span> of <span class="total"></span>' +
                                    '</div>' +
                                    '</div>' +
                                    '</div>';
        //init param
        var $images = options.images,
            $initImageIndex = options.initImageIndex,
            $scrollSwitch = options.scrollSwitch;

        if (!$images || !$images.length) return;
        if (!$initImageIndex) $initImageIndex = 1;
        var $nowImageIndex = $initImageIndex;
        //init dom
        if (!$('#pictureViewer').length) $('body').append(pictureViewer_html);
        //definition variable
        var BODY = $('body');
        var ESC_KEY_CODE = 27;
        var LEFT_KEY_CODE = 37;
        var RIGHT_KEY_CODE = 39;
        var $pictureViewer = $('#pictureViewer');
        var $pictureViewerContent = $pictureViewer.children('.content');
        var $cover = $pictureViewer.find('.picture-content .cover');
        var $closeBtn = $pictureViewer.find('.close-view');
        var $maximizationBtn = $pictureViewer.find('.maximization');
        var $miniaturizationBtn = $pictureViewer.find('.miniaturization');
        var $prevBtn = $pictureViewer.find('.handel-prev');
        var $nextBtn = $pictureViewer.find('.handel-next');
        var $num = $pictureViewer.find('.counter .num');
        var $total = $pictureViewer.find('.counter .total');
        var defaultViewWidth = $pictureViewerContent.css('width');
        var defaultViewHeight = $pictureViewerContent.css('height');
        var $imagesTotal = $images.length;
        //view is show
        var viewIsShow = function viewIsShow() {
            return $pictureViewer.is(':visible');
        };
        //lock body
        var lockBody = function lockBody() {
            return BODY.css('overflow', 'hidden');
        };
        //unlock body
        var unlockBody = function unlockBody() {
            return BODY.css('overflow', 'auto');
        };
        //show view
        var showView = function showView() {
            $pictureViewer.show();
            lockBody();
        };
        //hide view
        var hideView = function hideView() {
            $pictureViewer.hide();
            $maximizationBtn.show();
            $miniaturizationBtn.hide();
            $pictureViewerContent.css({ 'width': defaultViewWidth, 'height': defaultViewHeight });
            unlockBody();
        };
        //change image
        var changeImage = function changeImage(index) {
            $cover.attr('src', $images[index]);
            $nowImageIndex = index;
            changeImageNum();
        };
        //change image num
        var changeImageNum = function changeImageNum() {
            $num.text($nowImageIndex + 1);
        };
        //to prev image
        var toPrevImage = function toPrevImage() {
            return changeImage($nowImageIndex === 0 ? $imagesTotal - 1 : $nowImageIndex - 1);
        };
        //to next image
        var toNextImage = function toNextImage() {
            return changeImage($nowImageIndex === $imagesTotal - 1 ? 0 : $nowImageIndex + 1);
        };
        //init state
        showView();
        changeImage($initImageIndex - 1);
        $total.text($imagesTotal);
        //handle close click
        $closeBtn.on('click', hideView);
        //handel maximization click
        $maximizationBtn.on('click', function () {
            $(this).hide();
            $miniaturizationBtn.show();
            $pictureViewerContent.css({ 'width': '100%', 'height': '100%' });
        });
        //handel miniaturization click
        $miniaturizationBtn.on('click', function () {
            $(this).hide();
            $maximizationBtn.show();
            $pictureViewerContent.css({ 'width': defaultViewWidth, 'height': defaultViewHeight });
        });
        //handle document keyDown
        $(document).on('keydown', function (event) {
            if (!viewIsShow()) return;
            var keyCode = event.keyCode;

            if (keyCode === ESC_KEY_CODE) hideView();
            if (keyCode === LEFT_KEY_CODE) toPrevImage();
            if (keyCode === RIGHT_KEY_CODE) toNextImage();
        });
        //handel prev click
        $prevBtn.on('click', toPrevImage);
        //handel next click
        $nextBtn.on('click', toNextImage);

        if ($scrollSwitch) {
            try {
                $pictureViewerContent.mousewheel(function (event, delta) {
                    if (delta === 1) toPrevImage();
                    if (delta === -1) toNextImage();
                });
            } catch (e) {
                throw 'mousewheel plugin No import!';
            }
        }
    };
})(jQuery, document, window);