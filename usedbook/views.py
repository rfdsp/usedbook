# -*- coding: utf-8 -*-
from usedbook.models import WantedBook
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
import threading

class offer:
    isbn=''
    name=''
    price=''
    realPrice=''
    save=''
    link=''
    id=''
    def __init__(self):
        pass

class theOffersGetter(threading.Thread):
    def __init__(self,abook,result):
        threading.Thread.__init__(self)
        self.abook=abook
        self.result=result
    def run(self):
        from urllib2 import urlopen
        import re
        isbn=self.abook.isbn
        url=urlopen('http://used.aladin.co.kr/shop/UsedShop/wuseditemall.aspx?ISBN={POSISBN}'.format(POSISBN=isbn))
        raw=url.read()
        decoded=raw.decode('cp949')


        title_re=re.compile(r"<a href='http://www.aladin.co.kr/shop/wproduct.aspx\?ISBN=.*?' class='p_topt01'>(.*?)</a>".decode('utf-8'))
        title=title_re.findall(decoded)[0]
        newbookretailPrice_re=re.compile(r'정가</td>\r\n  <td valign="top" class="p_goodstd02">([\d,]*?)원'.decode('utf-8'))
        newbookPrice_re=re.compile(r'판매가</td>\r\n  <td valign="top" class="p_goodstd02">\r\n      <span class="p_new_price_phs">([\d,]*?)원'.decode('utf-8'))
        newbookMillage_re=re.compile(r'마일리지</td>\r\n  <td valign="top" class="p_goodstd02">([\d,]*?)점'.decode('utf-8'))

        retailPrice=int(newbookretailPrice_re.findall(decoded)[0].replace(',',''))
        price=int(newbookPrice_re.findall(decoded)[0].replace(',',''))
        millage=int(newbookMillage_re.findall(decoded)[0].replace(',',''))
        realPrice=price-millage


        price_re=re.compile('(<a href="http://used.aladin.co.kr/shop/wproduct.aspx\?ItemId=.*?" class="bo".*?></a>)[\s\S]*?<span class="ss_p2"><b>([\d,]*)[\s\S]*?(<a.*?</a>)')
        pricelist=price_re.findall(decoded)
        theoffers=list()
        for link,price,seller in pricelist:
            price=int(price.replace(',',''))
            aoffer=offer()
            aoffer.seller=seller.replace('href="','href="http://www.aladin.co.kr')
            aoffer.name=title
            aoffer.price=price
            aoffer.isbn=isbn
            aoffer.link=link
            aoffer.realPrice=realPrice
            aoffer.id=self.abook.id
            aoffer.save=(realPrice-price)*100.0/realPrice
            theoffers.append(aoffer)
        self.result.append(theoffers)



def index(request):
    wanted_book_list = WantedBook.objects.all().order_by('isbn')
    return render_to_response('usedbook/index.html',
                              {'wanted_book_list': wanted_book_list},
                              context_instance=RequestContext(request))

def add(request):
    try:
        isbn=request.POST['isbn']
    except :
        error_msg='ISBN값을 입력해 주십시요'
    else:
        if(len(isbn)!=10):
            error_msg='{0}은 ISBN-10이 아닙니다. ISBN-10을 입력해 주십시요.'.format(isbn)
        else:
            from urllib2 import urlopen
            import re
            url=urlopen('http://used.aladin.co.kr/shop/UsedShop/wuseditemall.aspx?ISBN={POSISBN}'.format(POSISBN=isbn))
            raw=url.read()
            decoded=raw.decode('cp949')
            title_re=re.compile(r"<a href='http://www.aladin.co.kr/shop/wproduct.aspx\?ISBN=.*?' class='p_topt01'>(.*?)</a>".decode('utf-8'))
            title=title_re.findall(decoded,)
            if(not title):
                return HttpResponse('----ISBN-10(10자리)  {POSISBN} 에 해당하는 유효한 상품정보가 없습니다.----'.format(POSISBN=isbn))


            newbookretailPrice_re=re.compile(r'정가</td>\r\n  <td valign="top" class="p_goodstd02">([\d,]*?)원'.decode('utf-8'))
            newbookPrice_re=re.compile(r'판매가</td>\r\n  <td valign="top" class="p_goodstd02">\r\n      <span class="p_new_price_phs">([\d,]*?)원'.decode('utf-8'))
            newbookMillage_re=re.compile(r'마일리지</td>\r\n  <td valign="top" class="p_goodstd02">([\d,]*?)점'.decode('utf-8'))

            
            new_book=WantedBook(isbn=isbn,name=title[0])
            new_book.retailPrice=int(newbookretailPrice_re.findall(decoded)[0].replace(',',''))
            new_book.price=int(newbookPrice_re.findall(decoded)[0].replace(',',''))
            new_book.millage=int(newbookMillage_re.findall(decoded)[0].replace(',',''))
            new_book.realPrice=new_book.price-new_book.millage
            try:
                new_book.save()
            except:
                return HttpResponse('글을 써넣다가 오류가 발생했습니다.')
        return HttpResponseRedirect(reverse('usedbook.views.index',args=()))


def result(request):
    offers=dict()
    wanted_book_list = WantedBook.objects.all().order_by('isbn')
    offerlist=[]
    threads=map(lambda x:theOffersGetter(x,offerlist),wanted_book_list)
    map(lambda x: x.start(),threads)
    map(lambda x: x.join(),threads)
    for theoffers in offerlist:
        for offer in theoffers:
            offers[offer.seller]=offers.get(offer.seller,[])
            offers[offer.seller].append(offer)

    offers=list(offers.items())
    offers.sort(key=lambda x:len(x[1]),reverse=True)

    return render_to_response('usedbook/result.html',
                              {'offers': offers},
                              context_instance=RequestContext(request))


def delete(request,wantedbook_id):
    book = get_object_or_404(WantedBook, pk=wantedbook_id)
    isbn=book.isbn
    error_msg='{0}제거합니다.'.format(isbn)
    book.delete()
    return HttpResponseRedirect(reverse('usedbook.views.index',args=()))

