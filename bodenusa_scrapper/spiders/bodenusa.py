import re
import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import json
from ..items import BodenusaScrapperItem

# Constants
FIT_KEYWORDS = ["Maternity", "Petite", "Plus Size", "Curvy", "Tall"]
NECK_LINE_KEYWORDS = ["Scoop", "Round Neck," "U Neck", "U-Neck", "V Neck",
                      "V-neck", "V Shape", "V-Shape", "Deep", "Plunge", "Square",
                      "Straight", "Sweetheart", "Princess", "Dipped", "Surplice",
                      "Halter", "Asymetric", "One-Shoulder", "One Shoulder",
                      "Turtle", "Boat", "Off- Shoulder", "Collared", "Cowl", "Neckline"]

OCCASIONS_KEYWORDS = ["office", "work", "smart", "workwear", "wedding", "nuptials",
                      "night out", "evening", "spring", "summer", "day", "weekend",
                      "outdoor", "outdoors", "adventure", "black tie", "gown",
                      "formal", "cocktail", "date night", "vacation", "vacay", "fit",
                      "fitness", "athletics", "athleisure", "work out", "sweat",
                      "swim", "swimwear", "lounge", "loungewear"]

LENGTH_KEYWORDS = ["length", "mini", "short", "maxi", "crop", "cropped", "sleeves",
                   "tank", "top", "three quarter", "ankle", "long"]

STYLE_KEYWORDS = ["bohemian", "embellished", "sequin", "floral", "off shoulder",
                  "puff sleeve", "bodysuit", "shell", "crop", "corset", "tunic",
                  "bra", "camisole", "polo", "aviator", "shearling", "sherpa",
                  "biker", "bomber", "harrington", "denim", "jean", "leather",
                  "military", "quilted", "rain", "tuxedo", "windbreaker", "utility",
                  "duster", "faux fur", "overcoat", "parkas", "peacoat", "puffer",
                  "skater", "trench", "Fleece", "a line", "bodycon", "fitted",
                  "high waist", "high-low", "pencil", "pleat", "slip", "tulle",
                  "wrap", "cargo", "chino", "skort", "cigarette", "culottes",
                  "flare", "harem", "relaxed", "skinny", "slim", "straight leg",
                  "tapered", "wide leg", "palazzo", "stirrup", "bootcut", "boyfriend",
                  "loose", "mom", "jeggings", "backless", "bandage", "bandeau",
                  "bardot", "one-shoulder", "slinger", "shift", "t-shirt", "smock",
                  "sweater", "gown"]

AESTHETIC_KEYWORDS = ["E-girl", "VSCO girl", "Soft Girl", "Grunge", "CottageCore",
                      "Normcore", "Light Academia", "Dark Academia ", "Art Collective",
                      "Baddie", "WFH", "Black", "fishnet", "leather"]

DISALLOWED_CATEGORY_KEYWORDS = [
    "baby", "shoes", "accessories", "joggers", "sandals", "men",
    "womens-tending-now", "womens-final-sale", "family-moments",
    "womens-trends-online", "mens-essentials", "mens-chino-shop", "girls-overalls",
    "back-to-school", "graphics-shop", "boys-essentials", "younger-boys", "older-boys",
    "girls-essentials", "mens-sweats", "girls-new-in", "mens-new-in", "womens-new-in",
    "boys-new-in", "womens-occasionwear", "boys", "embroidery-shop"]

WEBSITE_NAME = "bodenusa"

CATEGORY_KEYWORDS = ['Bottom', 'Shift', 'Swim Brief', 'Quilted', 'Boyfriend',
                     'Padded', 'Track', 'Other', 'Oversized', 'Denim Skirt',
                     'Stick On Bra', 'Cardigan', 'Thong', 'Romper', 'Pea Coat',
                     'Skater', 'Swing', 'Lingerie & Sleepwear', 'Wrap', 'Cargo Pant',
                     'Cape', 'Trucker', 'Nursing', 'Bikini', 'Parka', 'Regular', 'Denim',
                     'Duster', 'Faux Fur', 'Hoodie', 'Bralet', 'Overcoat', 'Corset Top',
                     'T-Shirt', 'Mini', 'Maxi', 'Blazer', 'Super Skinny', 'Summer Dresses',
                     'Chino', 'Short', 'Set', 'Military', 'Overall', 'Vest', 'Bomber Jacket',
                     'Tea', 'Ski Suit', 'Work Dresses', 'High Waisted', 'Culotte', 'Overall Dress',
                     'Jean', 'Loungewear', 'Leather Jacket', 'Unpadded', 'Coats & Jackets', 'Underwired',
                     'Corset', 'Night gown', 'Poncho', 'Pant', 'Cigarette', 'Sweatpant', 'Rain Jacket',
                     'Loose', 'Swimwear & Beachwear', 'Shirt', 'Denim Jacket', 'Co-ord', 'Tight', 'Vacation Dress',
                     'Harrington', 'Bandage', 'Bootcut', 'Biker', 'Crop Top', 'Trench', 'Tracksuit', 'Suit Pant',
                     'Relaxed', 'Day Dresses', 'Tuxedo', 'Tapered', 'Wide Leg', 'Bohemian', 'Pleated', 'Wiggle',
                     'One Shoulder', 'Smock Dress', 'Flare', 'Peg Leg', 'Cover Up', 'Unitard', 'Sweater',
                     'Lounge', 'Top', 'Bodycon', 'Push Up', 'Slip', 'Knitwear', 'Leather', 'Pencil Dress',
                     'Off Shoulder', 'Jersey Short', 'Multiway', 'Balconette', 'Wax Jacket', 'Coat', 'Brief',
                     'Coach', 'Jumpsuits & Rompers', 'Bra', 'Long Sleeve', 'Fleece', 'Activewear', 'Jegging',
                     'Outerwear', 'Bandeau', 'Slim', 'Going Out Dresses', 'Bardot', 'Pajama', 'Sweatsuit',
                     'Blouse', 'Sweaters & Cardigans', 'Straight Leg', 'Windbreaker', 'Tank Top', 'Cold Shoulder',
                     'Halter', 'Dresses', 'T-Shirt', 'Trouser', 'Cami', 'Camis', 'Wedding Guest', 'Bodysuit',
                     'Triangle',
                     'Casual Dresses', 'Chino Short', 'Boiler Suit', 'Raincoat', 'Formal Dresses', 'Skinny',
                     'Jumper', 'Strapless', 'Cropped', 'Jacket', 'Bridesmaids Dress', 'Tunic', 'A Line',
                     'Denim Dress', 'Cocktail', 'Skirt', 'Jumpsuit', 'Shapewear', 'Occasion Dresses',
                     'Hoodies & Sweatshirts', 'Sweatshirt', 'Aviator', 'Sweater Dress', 'Sports Short',
                     'Shirt', 'Puffer', 'Cargo Short', 'Tulle', 'Swimsuit', 'Mom Jean', 'Legging',
                     'Plunge', 'Teddie', 'Denim Short', 'Intimate', 'Pencil Skirt', 'Backless', 'Tank']

CATEGORY_TO_TYPE = {
    'Co-ords': ['Co-ord', 'Sweatsuit', 'Tracksuit', 'Set'],
    'Coats & Jackets': ['Coats & Jacket', 'Cape', 'Cardigan', 'Coat', 'Jacket', 'Poncho', 'Ski Suit', 'Vest', 'Blazer'],
    'Dresses': ['Dresses', 'Bridesmaids Dress', 'Casual Dress', 'Going Out Dress', 'Occasion Dress',
                'Summer Dress', 'Work Dress', 'Formal Dress', 'Day Dress', 'Wedding Guest', 'Vacation Dress'],
    'Hoodies & Sweatshirts': ['Hoodies & Sweatshirts', 'Fleece', 'Hoodie', 'Sweatshirt'],
    'Denim': ['Denim Jacket', 'Denim Dress', 'Denim Skirt', 'Denim Short', 'Jean', 'Jegging'],
    'Jumpsuits & Rompers': ['Jumpsuits & Rompers', 'Boiler Suit', 'Jumpsuit', 'Overall', 'Romper', 'Unitard'],
    'Lingerie & Sleepwear': ['Lingerie & Sleepwear', 'Intimate', 'Bra', 'Brief', 'Corset', 'Bralet', 'Night gown',
                             'Pajama', 'Shapewear', 'Slip', 'Teddie', 'Thong', 'Tight', 'Bodysuit', 'Camis', 'Cami'],
    'Loungewear': ['Loungewear', 'Lounge', 'Activewear', 'Outerwear', 'Hoodie', 'Legging', 'Overall', 'Pajama',
                   'Sweatpant', 'Sweatshirt', 'Tracksuit', 'T-Shirt'],
    'Bottoms': ['Bottom', 'Chino', 'Legging', 'Pant', 'Suit Pant', 'Sweatpant', 'Tracksuit', 'Short', 'Skirt',
                'Trouser'],
    'Sweaters & Cardigans': ['Sweaters & Cardigans', 'Sweatpant', 'Cardigan', 'Sweater', 'Knitwear'],
    'Swimwear & Beachwear': ['Swimwear & Beachwear', 'Bikini', 'Cover Up', 'Short', 'Skirt', 'Swim Brief', 'Swimsuit'],
    'Tops': ['Top', 'Blouse', 'Bodysuit', 'Bralet', 'Camis', 'Corset Top', 'Crop Top', 'Shirt', 'Sweater',
             'Tank Top', 'T-Shirt', 'Tunic'],
}

CATEGORY_TO_STYLE = {
  'Co-ords' : ['Co-ords'],
  'Coats & Jackets' : ['Coats & Jackets', 'Aviator', 'Biker', 'Bomber Jacket', 'Coach', 'Denim Jacket', 'Duster', 'Faux Fur', 'Harrington', 'Leather', 'Leather Jacket', 'Military', 'Other', 'Overcoat', 'Parkas', 'Pea Coat', 'Puffer', 'Quilted', 'Raincoats', 'Rain Jackets', 'Regular', 'Skater', 'Track', 'Trench', 'Trucker', 'Tuxedo', 'Wax Jacket', 'Windbreaker'],
  'Dresses' : ['Dresses', 'A Line', 'Backless', 'Bandage', 'Bandeau', 'Bardot', 'Bodycon', 'Bohemian', 'Cold Shoulder', 'Denim', 'Jumper', 'Leather', 'Long Sleeve', 'Off Shoulder', 'One Shoulder', 'Other', 'Overall Dress', 'Pencil Dress', 'Shift', 'Shirt', 'Skater', 'Slip', 'Smock Dresses', 'Sweater Dress', 'Swing', 'Tea', 'T-Shirt', 'Wiggle', 'Wrap', 'Cocktail', 'Maxi', 'Mini'],
  'Hoodies & Sweatshirts' : ['Hoodies & Sweatshirts'],
  'Denim' : ['Jeans', 'Bootcut', 'Boyfriend', 'Cropped', 'Flare', 'High Waisted', 'Loose', 'Mom Jeans', 'Other', 'Regular', 'Skinny', 'Slim', 'Straight Leg', 'Super Skinny', 'Tapered', 'Wide Leg'],
  'Jumpsuits & Rompers' : ['Jumpsuits & Rompers'],
  'Lingerie & Sleepwear' : ['Lingerie & Sleepwear', 'Balconette', 'Halter', 'Multiway', 'Nursing', 'Padded', 'Plunge', 'Push Up', 'Stick On Bra', 'Strapless', 'Triangle', 'T-Shirt', 'Underwired', 'Unpadded'],
  'Loungewear' : ['Loungewear'],
  'Bottoms' : ['Bottoms', 'Cargo Pants', 'Cigarette', 'Cropped', 'Culottes', 'Flare', 'High Waisted', 'Other', 'Oversized', 'Peg Leg', 'Regular', 'Relaxed', 'Skinny', 'Slim', 'Straight Leg', 'Super Skinny', 'Tapered', 'Wide Leg', 'Cargo Shorts', 'Chino Shorts', 'Denim', 'High Waisted', 'Jersey Shorts', 'Other', 'Oversized', 'Regular', 'Relaxed', 'Skinny', 'Slim', 'Sports Shorts', 'A Line', 'Bodycon', 'Denim', 'High Waisted', 'Other', 'Pencil Skirt', 'Pleated', 'Skater', 'Slip', 'Tulle', 'Wrap'],
  'Sweaters & Cardigans' : ['Sweaters & Cardigans'],
  'Swimwear & Beachwear' : ['Swimwear & Beachwear', 'Halter', 'High Waisted', 'Multiway', 'Padded', 'Plunge', 'Strapless', 'Triangle', 'Underwired'],
  'Tops' : ['Tops'],
}

class BodenusaSpider(scrapy.Spider):
    name = 'bodenusa'
    allowed_domains = ['www.bodenusa.com']

    def __init__(self, *a, **kw):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
        options.add_argument(f'user-agent={user_agent}')
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        super().__init__(*a, **kw)

    def start_requests(self):
        url = "https://www.bodenusa.com/en-us/"
        yield scrapy.Request(url=url, callback=self.parse)


    # This function parses category links for the site
    def parse(self, response):
        links = response.css(
            "div.menu-item-group-wrapper div.aem-Grid div div.menuItem a.menu-item__link::attr('href')").getall()
        links = [link for link in links if not self.in_disallowed_category_keywords(link)]
        for link in links:
            yield scrapy.Request(url=link, callback=self.parse_pages)

    # This function finds total number of products, and then yield request for each page
    def parse_pages(self, response):
        json_meta = json.loads(response.css("script#productGrid-data::text").get())
        total_products_str = json_meta["response"]["numFound"]
        total_products = 60
        if total_products_str:
            total_products = int(total_products_str)

        # Now we will yield request for each page
        page = 1
        for _ in range(0, total_products, 60):
            yield scrapy.Request(url=f"{response.request.url}?page={page}", callback=self.parse_products)
            page += 1

    # This function parses links for all products

    def parse_products(self, response):
        product_links = response.css("div.product-item a.product-item-link::attr('href')").getall()
        for product_link in product_links:
            yield scrapy.Request(url=product_link, callback=self.parse_product)

    # This function parses product details
    def parse_product(self, response):
        url = response.request.url
        product_meta = json.loads(response.css("script.pdp-seo-product-schema::text").get())
        product_name = response.css("span.product-title__main::text").get().strip()
        brand = product_meta["brand"]["name"]
        name = f"{brand} {product_name}" if brand else product_name
        external_id = product_meta["sku"]
        sizes = response.css("li.pdp-sku-selector__size-item span::text").getall()
        colors = response.css(".colour-swatches__item-content::attr('title')").getall()
        details = [product_meta["description"]]
        details_meta = response.css("ul.pdp-bullet-points li::text").getall()
        fabric = self.find_fabric_from_details(details_meta)
        images = response.xpath("//img[@class='image-gallery__thumbs-img lazyloaded'] /@data-src").getall()
        images = [image.replace("medium", "large") for image in images]
        scrapped_categories = response.css("ol.breadcrumbs-list li a::text").getall()[1:]
        categories = []
        extracted_categories = extract_categories_from(url)
        if extracted_categories:
            categories = find_actual_parent(scrapped_categories, extracted_categories)
        else:
            extracted_categories = extract_categories_from(name)
            if extracted_categories:
                categories = find_actual_parent(scrapped_categories, extracted_categories)
            else:
                extracted_categories = extract_categories_from(scrapped_categories)
                if extracted_categories:
                    categories = find_actual_parent(scrapped_categories, extracted_categories)

        fit = response.css("ul.pdp-sku-selector__fit-list li span::text").getall()
        if not fit:
            fit = ' '.join(self.find_keywords_from_str(details_meta, name, url, FIT_KEYWORDS))
        else:
            fit = ' '.join(fit)

        neck_line = ' '.join(self.find_keywords_from_str(details_meta,name, url, NECK_LINE_KEYWORDS)).strip()
        length = ' '.join(self.find_keywords_from_str(details_meta,name, url, LENGTH_KEYWORDS)).strip()
        occasions = self.find_keywords_from_str(details_meta,name, url, OCCASIONS_KEYWORDS)
        style = self.find_keywords_from_str(details_meta,name, url, STYLE_KEYWORDS)
        meta = {}

        # Getting data using selenium
        self.driver.get(response.request.url)
        self.driver.implicitly_wait(5)
        price = self.driver.find_element(By.CSS_SELECTOR, "p.product-price").text
        review_description_elems = self.driver.find_elements(By.CSS_SELECTOR, "p.pr-rd-description-text")
        review_description = [review_element.text for review_element in review_description_elems if review_element.text]
        gender = 'women'
        number_of_reviews = str(len(review_description)) if review_description else ""
        top_best_seller = ""
        # aesthetics = self.find_from_target_string_multiple(details, name, categories, AESTHETIC_KEYWORDS)

        item = BodenusaScrapperItem()
        item["url"] = response.request.url
        item["external_id"] = external_id
        item["categories"] = categories
        item["name"] = name
        item["price"] = price
        item["colors"] = colors
        item["sizes"] = sizes
        item["details"] = details
        item["fabric"] = fabric
        item["images"] = images
        item["fit"] = fit
        item["neck_line"] = neck_line
        item["length"] = length
        item["gender"] = gender
        item["number_of_reviews"] = number_of_reviews
        item["review_description"] = review_description
        item["top_best_seller"] = top_best_seller
        item["meta"] = meta
        item["occasions"] = occasions
        item["style"] = style
        item["website_name"] = WEBSITE_NAME
        # item["aesthetics"] = aesthetics
        if categories:
            if not self.in_disallowed_category_keywords(url, name, categories):
                yield item

    # This function checks if link passed to it as an argument has disallowed category keywords or not
    def in_disallowed_category_keywords(self, url, name="", categories=[]):
        for keyword in DISALLOWED_CATEGORY_KEYWORDS:
            if re.search(keyword, url, re.IGNORECASE) or re.search(keyword, name, re.IGNORECASE) or \
                    re.search(keyword, ' '.join(categories), re.IGNORECASE):
                return True

        return False

    # Helpers
    # This helper finds fabric from details and returns it
    def find_fabric_from_details(self, details):
        product_details = ' '.join(details)
        fabrics_founded = re.findall(r"""(\d+ ?%\s?)?(
            velvet\b|silk\b|satin\b|cotton\b|lace\b|
            sheer\b|organza\b|chiffon\b|spandex\b|polyester\b|
            poly\b|linen\b|nylon\b|viscose\b|Georgette\b|Ponte\b|
            smock\b|smocked\b|shirred\b|Rayon\b|Bamboo\b|Knit\b|Crepe\b|
            Leather\b|polyamide\b|Acrylic\b|Elastane\bTencel\bCashmere\b|Polyurethane\b|Rubber\b|Lyocell\b)\)?""",
                                     product_details,
                                     flags=re.IGNORECASE | re.MULTILINE)
        fabric_tuples_joined = [''.join(tups) for tups in fabrics_founded]
        # Removing duplicates now if any
        fabrics_final = []
        for fabric in fabric_tuples_joined:
            if fabric not in fabrics_final:
                fabrics_final.append(fabric)

        return ' '.join(fabrics_final).strip()


    def find_keywords_from_str(self, details, name, url, keywords):
        finals = []
        details = ' '.join(details)
        for keyword in keywords:
            if re.search(keyword, details, re.IGNORECASE) or re.search(keyword, name, re.IGNORECASE) or \
                    re.search(keyword, url, re.IGNORECASE):
                if keyword not in finals:
                    finals.append(keyword)

        return finals

# This function maps category we have extracted from name or url to taxonomy,
# and then it returns the list of extracted keywords.
def map_to_parents(cats):
    # where cats -> categories
    # cat -> category
    finals = []
    for cat in cats:
        for key in CATEGORY_TO_TYPE:
            if re.search(cat, ' '.join(CATEGORY_TO_TYPE[key]), re.IGNORECASE):
                finals.append(key)

    if not finals:
        for cat in cats:
            for key in CATEGORY_TO_STYLE:
                if re.search(cat, ' '.join(CATEGORY_TO_STYLE[key]), re.IGNORECASE):
                    finals.append(key)
    return list(set(finals))


# This function find real parent category from the list of extracted categories we provided
# Arguments: -> here first arg is scrapped categories and second is one which is list of extracted keywords
# we basically loop over scrapped categories and check if any category from scrapped one lies in extracted ones
def find_actual_parent(scrapped_cats, categories):
    finals = []
    final_categories = map_to_parents(categories)
    if len(final_categories) > 1:
        for fc in final_categories:
            if re.search(fc, ' '.join(scrapped_cats), re.IGNORECASE):
                finals.append(fc)

        if finals:
            return finals
        else:
            return []
    else:
        if final_categories:
            return final_categories
        else:
            return []


# This function extracts category keywords from product attribute passed as an argument to it
def extract_categories_from(keyword):
    cats = []  # categories
    if type(keyword) == list:
        keyword = ' '.join(keyword)

    for cat in CATEGORY_KEYWORDS:
        if re.search(cat, keyword, re.IGNORECASE):
            cats.append(cat)

    return cats


