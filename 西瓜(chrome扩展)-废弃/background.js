chrome.runtime.onInstalled.addListener(function(details){
    chrome.declarativeContent.onPageChanged.removeRules(undefined, function(){
        chrome.declarativeContent.onPageChanged.addRules([
            {
                conditions: [
                    //半次元
                    new chrome.declarativeContent.PageStateMatcher({pageUrl: {urlMatches: 'https://bcy\.net/item/detail/[0-9]+'}}),
                    //知乎专栏
                    new chrome.declarativeContent.PageStateMatcher({pageUrl: {urlMatches: 'https://zhuanlan\.zhihu\.com/p/[0-9]+'}}),
                    //我的小书屋
                    new chrome.declarativeContent.PageStateMatcher({pageUrl: {urlMatches: 'http://mebook\.cc/[0-9]+\.html'}}),
                    //简书
                    new chrome.declarativeContent.PageStateMatcher({pageUrl: {urlMatches: 'https://www\.jianshu\.com/p/[0-9a-zA-Z]+'}}),
                    //csdn
                    new chrome.declarativeContent.PageStateMatcher({pageUrl: {urlMatches: 'https://blog\.csdn\.net/[0-9a-zA-Z_]+?/article/details/[0-9]+'}}),
                    //掘金
                    new chrome.declarativeContent.PageStateMatcher({pageUrl: {urlMatches: 'https://juejin\.im/entry/[0-9a-zA-Z]+'}}),
                    //【旷世的忧伤】的博客
                    new chrome.declarativeContent.PageStateMatcher({pageUrl: {urlMatches: 'http://blog\.konghy\.cn/[0-9]{4}/[0-9]{2}/[0-9]{2}/*'}})
                ],
                actions: [new chrome.declarativeContent.ShowPageAction()]
            }
        ]);
    });
});

// 标识当前正在执行某个动作，并不是所有动作都会设置这个标志位
var action=null;

chrome.pageAction.onClicked.addListener(function(tab){
    host=tab.url.split('/')[2];
    console.log('host ==',host);
    if(host == 'mebook.cc'){
        action=host;
    }

    if(['bcy.net'].includes(host)){
        console.log('chrome.tabs.sendMessage with callback');
        var eName=prompt("请输入文件名",'default');
        if(eName == null){
            return;
        }
        var dir='图集/';
        chrome.tabs.sendMessage(tab.id,'start',function(response){
            if(response.imgs){
                for(let i=0;i<response.imgs.length;i++){
                    const e=response.imgs[i];
                    chrome.downloads.download({url:e,
                        filename:dir+(eName === 'default' ? e.replace(/.*\//,'') : eName+'_'+i+'.'+e.split('.').pop())});
                }
            }
        });
    }else{
        console.log('chrome.tabs.sendMessage');
        chrome.tabs.sendMessage(tab.id,'start');
    }
    
});

chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    console.log('onMessage: request =',request)
    if(request == 'action'){
        sendResponse(action)
    }else if(request == 'clear'){
        action = null;
    }
});

function printAttr(name,obj) {
    for (const key in obj) {
        if (obj.hasOwnProperty(key)) {
            console.log(`${name}.${key}: ${obj[key]}`);
        }
    }
}