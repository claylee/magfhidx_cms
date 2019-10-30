
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
