# pylint: disable=C0103, too-few-public-methods, locally-disabled, unused-variable,anomalous-backslash-in-string,no-self-use
'''wirralseafishing spiders'''
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader as _ItemLoader


import imgscrape.items as _items

import funclib.stringslib as stringslib


#These not picked up in first rum
_START_URLS = ['https://www.theyworkforyou.com/search/?q=Lidington+David', 'https://www.theyworkforyou.com/search/?q=Prentis+Victoria', 'https://www.theyworkforyou.com/search/?q=Jarvis+Dan', 'https://www.theyworkforyou.com/search/?q=Phillips+Jess', 'https://www.theyworkforyou.com/search/?q=Qureshi+Yasmin', 'https://www.theyworkforyou.com/search/?q=Lee+Phillip', 'https://www.theyworkforyou.com/search/?q=Pickles+Eric', 'https://www.theyworkforyou.com/search/?q=Liddell-Grainger+Ian', 'https://www.theyworkforyou.com/search/?q=Percy+Andrew', 'https://www.theyworkforyou.com/search/?q=Lucas+Caroline', 'https://www.theyworkforyou.com/search/?q=Leslie+Charlotte', 'https://www.theyworkforyou.com/search/?q=Neill+Bob', 'https://www.theyworkforyou.com/search/?q=Javid+Sajid', 'https://www.theyworkforyou.com/search/?q=Nuttall+David', 'https://www.theyworkforyou.com/search/?q=Lewis+Ivan', 'https://www.theyworkforyou.com/search/?q=Churchill+Jo', 'https://www.theyworkforyou.com/search/?q=Poulter+Daniel', 'https://www.theyworkforyou.com/search/?q=Perkins+Toby', 'https://www.theyworkforyou.com/search/?q=Jones+Susan Elan', 'https://www.theyworkforyou.com/search/?q=Jones+David', 'https://www.theyworkforyou.com/search/?q=Quince+Will', 'https://www.theyworkforyou.com/search/?q=Pursglove+Tom', 'https://www.theyworkforyou.com/search/?q=Philp+Chris', 'https://www.theyworkforyou.com/search/?q=Johnson+Gareth', 'https://www.theyworkforyou.com/search/?q=Perry+Claire', 'https://www.theyworkforyou.com/search/?q=Wood+Mike', 'https://www.theyworkforyou.com/search/?q=Law+Chris', 'https://www.theyworkforyou.com/search/?q=Pound+Stephen', 'https://www.theyworkforyou.com/search/?q=Nicolson+John', 'https://www.theyworkforyou.com/search/?q=Loughton+Tim', 'https://www.theyworkforyou.com/search/?q=Laing+Eleanor', 'https://www.theyworkforyou.com/search/?q=Pearce+Teresa', 'https://www.theyworkforyou.com/search/?q=Lopresti+Jack', 'https://www.theyworkforyou.com/search/?q=Leigh+Edward', 'https://www.theyworkforyou.com/search/?q=Lewis+Brandon', 'https://www.theyworkforyou.com/search/?q=Pennycook+Matthew', 'https://www.theyworkforyou.com/search/?q=Lynch+Holly', 'https://www.theyworkforyou.com/search/?q=Jones+Andrew', 'https://www.theyworkforyou.com/search/?q=Jenkin+Bernard', 'https://www.theyworkforyou.com/search/?q=Penning+Mike', 'https://www.theyworkforyou.com/search/?q=Norman+Jesse', 'https://www.theyworkforyou.com/search/?q=Prisk+Mark', 'https://www.theyworkforyou.com/search/?q=Lilley+Peter', 'https://www.theyworkforyou.com/search/?q=West+Catherine', 'https://www.theyworkforyou.com/search/?q=Quin+Jeremy', 'https://www.theyworkforyou.com/search/?q=Phillipson+Bridget', 'https://www.theyworkforyou.com/search/?q=Jones+Graham', 'https://www.theyworkforyou.com/search/?q=Johnson+Diana', 'https://www.theyworkforyou.com/search/?q=Johnson+Alan', 'https://www.theyworkforyou.com/search/?q=Powell+Lucy', 'https://www.theyworkforyou.com/search/?q=Kaufman+Gerald', 'https://www.theyworkforyou.com/search/?q=Jones+Gerald', 'https://www.theyworkforyou.com/search/?q=Latham+Pauline', 'https://www.theyworkforyou.com/search/?q=Lancaster+Mark', 'https://www.theyworkforyou.com/search/?q=Jenkyns+Andrea', 'https://www.theyworkforyou.com/search/?q=Lewis+Julian', 'https://www.theyworkforyou.com/search/?q=Jenrick+Robert', 'https://www.theyworkforyou.com/search/?q=Jones+Kevan', 'https://www.theyworkforyou.com/search/?q=Jayawardena+Ranil', 'https://www.theyworkforyou.com/search/?q=Lamb+Norman', 'https://www.theyworkforyou.com/search/?q=Paterson+Owen', 'https://www.theyworkforyou.com/search/?q=Lewis+Clive', 'https://www.theyworkforyou.com/search/?q=Leslie+Chris', 'https://www.theyworkforyou.com/search/?q=Jones+Marcus', 'https://www.theyworkforyou.com/search/?q=Johnson+Jo', 'https://www.theyworkforyou.com/search/?q=Newlands+Gavin', 'https://www.theyworkforyou.com/search/?q=Jackson+Stewart', 'https://www.theyworkforyou.com/search/?q=Lumley+Karen', 'https://www.theyworkforyou.com/search/?q=Nokes+Caroline', 'https://www.theyworkforyou.com/search/?q=Pawsey+Mark', 'https://www.theyworkforyou.com/search/?q=Long-Bailey+Rebecca', 'https://www.theyworkforyou.com/search/?q=Phillips+Stephen', 'https://www.theyworkforyou.com/search/?q=Leadsom+Andrea', 'https://www.theyworkforyou.com/search/?q=Lewell-Buck+Emma', 'https://www.theyworkforyou.com/search/?q=Pugh+John', 'https://www.theyworkforyou.com/search/?q=Lefroy+Jeremy', 'https://www.theyworkforyou.com/search/?q=Paterson+Steven', 'https://www.theyworkforyou.com/search/?q=James+Margot', 'https://www.theyworkforyou.com/search/?q=Pincher+Christopher', 'https://www.theyworkforyou.com/search/?q=Pow+Rebecca', 'https://www.theyworkforyou.com/search/?q=Pritchard+Mark', 'https://www.theyworkforyou.com/search/?q=Parish+Neil', 'https://www.theyworkforyou.com/search/?q=Lammy+David', 'https://www.theyworkforyou.com/search/?q=Newton+Sarah', 'https://www.theyworkforyou.com/search/?q=Johnson+Boris', 'https://www.theyworkforyou.com/search/?q=Lavery+Ian', 'https://www.theyworkforyou.com/search/?q=Jones+Helen', 'https://www.theyworkforyou.com/search/?q=Letwin+Oliver', 'https://www.theyworkforyou.com/search/?q=Penrose+John', 'https://www.theyworkforyou.com/search/?q=Nandy+Lisa', 'https://www.theyworkforyou.com/search/?q=Patel+Priti', 'https://www.theyworkforyou.com/search/?q=Lord+Jonathan', 'https://www.theyworkforyou.com/search/?q=Lucas+Ian']
_NAMES = ['David Lidington', 'Victoria Prentis', 'Dan Jarvis', 'Jess Phillips', 'Yasmin Qureshi', 'Phillip Lee', 'Sir Eric Pickles', 'Ian Liddell-Grainger', 'Andrew Percy', 'Caroline Lucas', 'Charlotte Leslie', 'Bob Neill', 'Sajid Javid', 'David Nuttall', 'Ivan Lewis', 'Jo Churchill', 'Daniel Poulter', 'Toby Perkins', 'Susan Elan Jones', 'David Jones', 'Will Quince', 'Tom Pursglove', 'Chris Philp', 'Gareth Johnson', 'Claire Perry', 'Mike Wood', 'Chris Law', 'Stephen Pound', 'John Nicolson', 'Tim Loughton', 'Eleanor Laing', 'Teresa Pearce', 'Jack Lopresti', 'Sir Edward Leigh', 'Brandon Lewis', 'Matthew Pennycook', 'Holly Lynch', 'Andrew Jones', 'Bernard Jenkin', 'Mike Penning', 'Jesse Norman', 'Mark Prisk', 'Peter Lilley', 'Catherine West', 'Jeremy Quin', 'Bridget Phillipson', 'Graham Jones', 'Diana Johnson', 'Alan Johnson', 'Lucy Powell', 'Sir Gerald Kaufman', 'Gerald Jones', 'Pauline Latham', 'Mark Lancaster', 'Andrea Jenkyns', 'Julian Lewis', 'Robert Jenrick', 'Kevan Jones', 'Ranil Jayawardena', 'Norman Lamb', 'Owen Paterson', 'Clive Lewis', 'Chris Leslie', 'Marcus Jones', 'Jo Johnson', 'Gavin Newlands', 'Stewart Jackson', 'Karen Lumley', 'Caroline Nokes', 'Mark Pawsey', 'Rebecca Long-Bailey', 'Stephen Phillips', 'Andrea Leadsom', 'Emma Lewell-Buck', 'John Pugh', 'Jeremy Lefroy', 'Steven Paterson', 'Margot James', 'Christopher Pincher', 'Rebecca Pow', 'Mark Pritchard', 'Neil Parish', 'David Lammy', 'Sarah Newton', 'Boris Johnson', 'Ian Lavery', 'Helen Jones', 'Oliver Letwin', 'John Penrose', 'Lisa Nandy', 'Priti Patel', 'Jonathan Lord', 'Ian Lucas']
#Merge these two if run again


class MPNames(CrawlSpider):
    '''scrape images from goangling.co.uk
    '''
    name = "mp-details"
    allowed_domains = ['parliament.uk']
    start_urls = ['http://www.parliament.uk/mps-lords-and-offices/mps/']
    rules = (Rule(LinkExtractor(restrict_xpaths='//div[@class="inner"]'), callback='parse_mp_page'),)

    def parse_mp_page(self, response):
        '''extract mp info in posts'''
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)
        urls = response.xpath('//div["id=ctl00_ctl00_FormContent_SiteSpecificPlaceholder_PageContent_ctlMainBody_wrapperDiv"]/div/p/a/@href').extract()
        names = response.xpath('//div["id=ctl00_ctl00_FormContent_SiteSpecificPlaceholder_PageContent_ctlMainBody_wrapperDiv"]/div/p/a/text()').extract()

        for ind, url in enumerate(urls):
            print(ind, url)
            yield scrapy.Request(url, callback=self.parse_mp_details, meta={'name':names[ind], 'url':url}, dont_filter=True)


    #Item Loads for Item MPDetails
    def parse_mp_details(self, response):
        '''get individual details'''
        n = response.meta.get('name')
        assert isinstance(n, str)
        n = n.split(',')

        names = [stringslib.trim(s, ' ') for s in n]
        #use our own item loaders, which inherits from the base.
        #ldrMPDetails specifies input and output handlers
        l = _items.ldrMPDetails(item=_items.itmMPDetails(), response=response)
        l.add_value('firstname', names[0])
        l.add_value('surname', names[-1])
        l.add_xpath('party', '//div[contains(@class,"contact-detail commons-party-list")]/ul/li/text()')
        l.add_xpath('constituency', '//div[contains(@class,"contact-detail commons-constituency-list")]/ul/li/text()')
        return l.load_item()


class MPVotesFox(CrawlSpider):
    '''given links, do search and get link to MP
    '''
    name = "mp-vote-fox"
    allowed_domains = ['theyworkforyou.com']
    policy = 'fox hunting'
    def start_requests(self):
        urls = _START_URLS
        for ind, url in enumerate(urls):
            yield scrapy.Request(url, callback=self.mp_search_results, dont_filter=True, meta={'name':_NAMES[ind], 'url':url})


    def mp_search_results(self, response):
        '''Need to build urls to the vote page
        Yields:https://www.theyworkforyou.com/mp/10133/jeremy_corbyn/islington_north/votes
        '''
        name = response.meta.get('name', '')

        assert isinstance(response, scrapy.http.response.html.HtmlResponse)

        link = response.selector.xpath('//div[@class="search-result search-result--person"]/h3[contains(@class, "search-result__title")]/a/@href').extract()[0]

        if link:
            link = 'https://www.theyworkforyou.com/' + link + '/divisions?policy=1050' #this is the fox policy
            yield scrapy.Request(link, callback=self.parse_stance, dont_filter=True, meta={'name':name})
        else:
            mp = _ItemLoader(_items.policy_vote)
            mp.add_value('name', name + ' NOT FOUND IN SEARCH')
            yield mp.load_item()


    def parse_stance(self, response):
        '''Parse stance from stance page. policy=? defines the vote.
        policy=1050 is the fox vote for example
        Expects eg:
        https://www.theyworkforyou.com/mp/10133/jeremy_corbyn/islington_north/divisions?policy=1050
        '''
        assert isinstance(response, scrapy.http.response.html.HtmlResponse)

        name = response.meta.get('name', '')

        #use the base itemloader as the policy_vote item specifies
        #the input/output handlers
        mp = _items.policy_vote_ldr(item=_items.policy_vote(), response=response)
        mp.add_value('name', name)
        mp.add_value('policy', MPVotesFox.policy)

        novote = response.xpath("//*[text()[contains(.,'has not voted on this policy')]]").extract()
        if novote:
            mp.add_value('stance', 'not voted')
        else:
            mp.add_xpath('stance', '//h3[@class="policy-vote-overall-stance"]/text()')


        return mp.load_item()
