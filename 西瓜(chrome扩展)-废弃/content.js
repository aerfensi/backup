const TAG='watermelon:';
chrome.runtime.onMessage.addListener(function(message, sender, sendResponse){
    var response={
        // imgs:array,
    };
    switch(location.host){
        case 'bcy.net':
            response.imgs=[];
            $('.img-wrap-inner>img').each(function(){
                response.imgs.push($(this).attr('src').slice(0,-5));
            });
            console.log(TAG,'onMessage : response =',response);
            sendResponse(response);
            break;
        case 'mebook.cc':
            if (location.href.match(/https?:\/\/mebook.cc\/\d+\.html/)) {
                location.href=$('a.downbtn').attr('href');
            }
            break;
        case 'zhuanlan.zhihu.com':
            $('.ColumnPageHeader-Wrapper').remove();
            $('.TitleImage').remove();
            $('.Recommendations-Main').remove();
            $('.Comments-container').remove();
            $('.Sticky.RichContent-actions.is-fixed.is-bottom').remove();
            $('.CornerButtons').remove();
            $('body').css({"font-family":"Noto Sans CJK SC"});
            $('code').css({"font-family":"mononoki"});
            window.print();
            break;
        case 'www.jianshu.com':
            $('.navbar').remove();
            $('.article').nextAll().remove()
            $('.note-bottom').remove();
            $('.side-tool').remove();
            $('#web-note-ad-fixed > span').click();
            window.print();
            break;
        case 'blog.csdn.net':
            $('aside').remove();
            $('header').remove();
            $('#csdn-toolbar').remove();
            $('.tool-box').remove();
            $('.pulllog-box').remove();
            $('.comment-box').remove();
            $('.t0').remove();
            $('.recommend-box').remove();
            window.print();
            break;
        case 'juejin.im':
            $('.main-header-box').remove();
            $('.comment-box').remove();
            $('.footer').remove();
            $('.entry-public-aside').remove();
            $('.article-suspended-panel').remove();
            $('.mobile-bottom-bar').remove();
            $('.thumb-placeholder').remove();
            $('.suspension-panel').remove();
            $('.entry-public-main>div:first-child').remove();
            window.print();
            break;
        case 'blog.konghy.cn':
            $('#header').remove();
            $('.pure-u-1-4').remove();
            $('#rocket').remove();
            $('#footer').remove();
            window.print();
            break;
    }
});


/*
mebook.cc
会发送两种消息到background page
1. action：请求获得当前action
2. clear：动作执行完毕，请求清除action
*/
if(location.href.match(/https?:\/\/mebook\.cc\/download\.php\?id=[0-9]+/)){
    chrome.runtime.sendMessage('action', function(response) {
        if(response == 'mebook.cc'){
            baiduyunCode=$('div.desc>p:nth-child(7)').text().match(/.*?(\w+)\s+.*/)[1];
            chrome.storage.local.set({'baiduyunCode':baiduyunCode},function(){
                // 跳转到百度云
                location.href = $('div.list>a:first-child').attr('href');
            });
        }
    });
}

if(location.host == 'pan.baidu.com'){
    chrome.runtime.sendMessage('action', function(response) {
        if(response == 'mebook.cc'){
            chrome.storage.local.get('baiduyunCode',function(items){
                $('body>div>div>div:nth-child(2) >form>div:nth-child(2)>dl>dd>input').attr('value',items['baiduyunCode']);
                $('.g-button-right').click();
                chrome.runtime.sendMessage('clear');
            })
        }
    });
}

// 工具函数

function printAttr(name,obj) {
    for (const key in obj) {
        if (obj.hasOwnProperty(key)) {
            console.log(`${name}.${key}: ${obj[key]}`);
        }
    }
}
