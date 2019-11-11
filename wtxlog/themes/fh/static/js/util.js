
function gethits(id, out)
{
  //$('#'+out).html("<img src=\"/_themes/imtx/images/loading.gif\" />");
  $.ajax({
    type: "get",
    cache:false,
    url: '/api/gethits/?id='+id,
    timeout: 20000,
    error: function(e){$('#'+out).html('failed');alert(e);},
    success: function(t){$('#'+out).html(t);alert(t);}
  });
}


function fanyi(id){
  no = $("#"+id).attr('no');
  $.ajax({
    url:'/fanyiname/'+no
  }).done(function(e){
    $("[no='"+no+"']").text(e);
  }).fail(function(e){
    console.log(e)
  });
}


(function ($) {
    var ms = {
        init: function (totalsubpageTmep, args) {
            return (function () {
                ms.fillHtml(totalsubpageTmep, args);
                ms.bindEvent(totalsubpageTmep, args);
            })();
        },
        //填充html
        fillHtml: function (totalsubpageTmep, args) {
            return (function () {
                totalsubpageTmep = "";
                link_to = "javascript:void(0);";

                // 页码大于等于4的时候，添加第一个页码元素
                if (args.currPage != 1 && args.currPage >= 4 && args.totalPage != 4) {
                    link_to = args.link_to.replace("__id__",1)
                    totalsubpageTmep += "<li class='page-item ali'><a href='"+link_to+"' class='page-link geraltTb_pager' data-go='' >" + 1 + "</a></li>";
                }
                /* 当前页码>4, 并且<=总页码，总页码>5，添加“···”*/
                if (args.currPage - 2 > 2 && args.currPage <= args.totalPage && args.totalPage > 5) {
                    totalsubpageTmep += "<li class='page-item ali'><a href='"+link_to+"' class='page-link geraltTb_' data-go='' >...</a></li>";
                }
                /* 当前页码的前两页 */
                var start = args.currPage - 2;
                /* 当前页码的后两页 */
                var end = args.currPage + 2;

                if ((start > 1 && args.currPage < 4) || args.currPage == 1) {
                    end++;
                }
                if (args.currPage > args.totalPage - 4 && args.currPage >= args.totalPage) {
                    start--;
                }
                for (; start <= end; start++) {
                    if (start <= args.totalPage && start >= 1) {
                        link_to = args.link_to.replace("__id__",start)
                        if (start == args.currPage)
                            totalsubpageTmep += "<li class='page-item ali active'><a href='"+link_to+"' class='page-link geraltTb_pager' data-go='' >" + start + "</a></li>";
                        else
                            totalsubpageTmep += "<li class='page-item ali'><a href='"+link_to+"' class='page-link geraltTb_pager' data-go='' >" + start + "</a></li>";
                    }
                }
                if (args.currPage + 2 < args.totalPage - 1 && args.currPage >= 1 && args.totalPage > 5) {
                    totalsubpageTmep += "<li class='page-item ali'><a href='"+link_to+"' class='page-link geraltTb_' data-go='' >...</a></li>";
                }

                if (args.currPage != args.totalPage && args.currPage < args.totalPage - 2 && args.totalPage != 4) {
                    link_to = args.link_to.replace("__id__",args.totalPage)
                    totalsubpageTmep += "<li class='page-item ali'><a href='"+link_to+"' class='page-link geraltTb_pager' data-go='' >" + args.totalPage + "</a></li>";
                }
                $(".pagination").html(totalsubpageTmep);
            })();
        },
        //绑定事件
        bindEvent: function (totalsubpageTmep, args) {
            return (function () {
                totalsubpageTmep.on("click", "a.geraltTb_pager", function (event) {
                    var current = parseInt($(this).text());
                    ms.fillHtml(totalsubpageTmep, { "currPage": current, "totalPage": args.totalPage, "turndown": args.turndown });
                    if (typeof (args.backFn) == "function") {
                        args.backFn(current);
                    }
                });
            })();
        }
    }
    $.fn.createPage = function (options) {
        ms.init(this, options);
    }
})(jQuery);
