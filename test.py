




from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.utils import platform
from plyer import sms
import pyrebase
import os
from openai import OpenAI

# Initialize Firebase (ensure your credentials file is correctly placed)
firebase_config = {
    "apiKey": "AIzaSyC8FcAwCdAHhpu0fZrdcoomE-XEtnKM9I4",
    "authDomain": "expense-tracker-mark1.firebaseapp.com",
    "projectId": "expense-tracker-mark1",
    "storageBucket": "expense-tracker-mark1.appspot.com",
    "messagingSenderId": "340133335397",
    "appId": "1:340133335397:web:cacece39ea50307f40518c",
    "measurementId": "G-ZXQZR9LPTC",
    "databaseURL": "https://expense-tracker-mark1-default-rtdb.firebaseio.com"
}

firebase = pyrebase.initialize_app(firebase_config)
db = firebase.database()


# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")

class MainScreen(Screen):
    pass

class SMSScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(on_pre_enter=self.check_permissions)

    def check_permissions(self, *args):
        if platform == 'android':
            try:
                from android.permissions import request_permissions, Permission
                permissions = [Permission.READ_SMS]
                request_permissions(permissions, self.permission_callback)
            except ImportError:
                self.ids.sms_label.text = "Error: Android permissions module not found."
        else:
            self.ids.sms_label.text = "SMS Feature requires Android."

    def permission_callback(self, permissions, results):
        if all(results):
            self.ids.sms_label.text = "SMS Permission Granted. New messages will be processed."
            self.listen_for_sms()
        else:
            self.ids.sms_label.text = "SMS Permission Denied. Cannot access messages."

    def listen_for_sms(self):
        if platform == 'android':
            sms.start_listening(self.on_sms_received)
        else:
            self.ids.sms_label.text += "\nSMS Listening not implemented for this platform."

    def on_sms_received(self, **kwargs):
        # This function will be called when a new SMS is received (Android only)
        if 'body' in kwargs:
            message_body = kwargs['body']
            # Assuming bank messages have a specific sender or keywords
            if "HDFC Bank" in kwargs.get('sender', ''):
                self.parse_sms(message_body)

    def parse_sms(self, message):
        p1 = f"""
        from the string "{message}" tell me how much is the amount paid, to whom is it paid, and then the date it was paid.
        also, categorise the recipient (to whom the amount was paid) into one of the following categories.
        Answer with this format only:

        - amount paid: how much is the amount paid - (digits only, you can use decimals) (if not mentioned reply with "not mentioned")
        - recipient: to whom is it paid (if not mentioned reply with "not mentioned")
        - date: the date it was paid (if not mentioned reply with "not mentioned")
        - category: categorise the recipient into one of the following categories -
        Food & Beverage, Transportation, Housing, Personal Care, Healthcare, Entertainment, Shopping, Education, Finance, Travel, Insurance, Household, Childcare,
        Pets, Miscellaneous, Subscriptions, Dining Out, Services, Professional Services, Fitness & Wellness, Utilities, Leisure & Recreation, Technology,
        Business Expenses, Social, Outdoor & Adventure, Home Improvement, Communication, Legal, Charity & Donations, Alcohol & Tobacco, Investment, Environmental,
        Religious, Seasonal, Hobbies & Crafts, Automotive, Maintenance & Repairs, Arts & Culture, Fashion & Apparel, Media & Publications, Digital Services, Fitness Equipment,
        Wellness & Nutrition, Taxes, Government Fees, Luxury, Self-care, DIY & Projects.
        - sub category:
        make sure that the subcategory falls under the respective core category. below, i have mentioned which sub categories
        fall under which core categories -
        Food & Beverage: Groceries, Restaurants, Cafes, Fast Food, Snacks, Bars & Alcohol, Food Delivery, Catering Services, Meal Kits, Vending Machines, Organic Produce, Food Trucks
        Transportation: Fuel, Public Transport, Ride-Hailing, Parking, Tolls, Vehicle Rentals, Carpooling, Bicycle Rentals, Vehicle Maintenance, Taxis, Scooter Rentals, Charging Stations, Airfare
        Housing: Rent, Mortgage, Utilities (Electricity, Water, Gas), Home Maintenance, Repairs, Property Taxes, Home Insurance, Renovations, Home Security, Landscaping, Homeowners Association Fees, Pest Control
        Personal Care: Gym Membership, Beauty & Spa, Haircuts, Skincare, Massage Therapy, Salon Services, Fitness Classes, Nail Care, Cosmetics, Perfumes, Health Retreats, Personal Grooming
        Healthcare: Doctor Visits, Medications, Health Insurance, Dental Care, Vision Care, Hospital Bills, Medical Equipment, Mental Health Services, Pharmaceuticals, Therapy, Rehabilitation, Alternative Medicine
        Entertainment: Movies, Concerts, Events, Hobbies, Recreation, Streaming Services, Gaming, Sports, Theatre, Nightlife, Amusement Parks, Museums, Bowling, Karaoke, Online Gaming, Board Games, Theme Parks
        Shopping: Clothing, Electronics, Accessories, Home Goods, Furniture, Jewelry, Books, Gifts, Office Supplies, Gadgets, Makeup, Shoes, Sporting Goods, Baby Products, Stationery, Party Supplies, Toys, Souvenirs, Garden Supplies
        Education: Tuition, Books, Courses, Seminars, Online Learning, Workshops, Exams, School Supplies, Extracurriculars, Learning Subscriptions, Professional Certifications, Study Abroad Programs, School Uniforms, Private Tutoring, Exam Fees
        Finance: Investments, Loans, Taxes, Banking Fees, Credit Card Payments, Savings Accounts, Financial Planning, Stock Trading, Crypto Investments, Mortgage Payments, Retirement Contributions, Mutual Funds
        Travel: Flights, Hotels, Vacation Rentals, Travel Insurance, Car Rentals, Cruises, Tours, Train Tickets, Travel Gear, Souvenirs, Excursions, Baggage Fees, Camping Equipment, Travel Guides, Visa & Passport Fees
        Insurance: Auto Insurance, Health Insurance, Home Insurance, Travel Insurance, Life Insurance, Disability Insurance, Pet Insurance, Renter’s Insurance, Boat Insurance, Business Insurance, Legal Insurance, Extended Warranties
        Household: Cleaning Supplies, Home Decor, Furniture, Appliances, Kitchenware, Linens, Storage Solutions, Lighting, Maintenance Equipment, Pest Control Products, Cleaning Services, Garden Tools, Cookware
        Childcare: Daycare, Babysitting, School Fees, Tutoring, Extracurricular Activities, Kids’ Clothing, Toys, Books, Pediatrician Visits, Baby Gear, Nannies, School Lunches, Field Trips, Camp Fees
        Pets: Vet Bills, Pet Food, Grooming, Pet Toys, Pet Insurance, Boarding, Pet Accessories, Adoption Fees, Pet Training, Pet Treats, Veterinary Medicine, Pet Sitters
        Miscellaneous: Unclassified, Special Occasions, Unforeseen Expenses, One-Time Purchases, Donations, Gifts, Unexpected Bills, Penalties & Fines
        Subscriptions: Streaming Services, Gaming, Magazines, Newspapers, Software, Cloud Services, Food Delivery, Beauty Boxes, Fitness Apps, Educational Subscriptions
        Dining Out: Restaurants, Cafes, Fast Food, Fine Dining, Casual Dining, Buffets, Bistros, Bakeries, Bars, Pubs, Food Trucks, Pop-Up Restaurants, Street Food
        Services: Cleaning Services, Landscaping, Pest Control, Moving Services, Interior Design, Home Staging, Maintenance Services, Event Planning, Personal Assistant, Delivery Services
        Professional Services: Legal Advice, Accounting Services, Consulting, Tax Preparation, Business Coaching, HR Services, IT Support, Graphic Design, Marketing Services, Financial Consulting
        Fitness & Wellness: Yoga Classes, Personal Training, Fitness Subscriptions, Fitness Gear, Wellness Retreats, Meditation Apps, Spa Treatments, Nutritional Counseling, Physical Therapy, Fitness Challenges
        Utilities: Electricity, Water, Gas, Internet, Cable, Phone Services, Waste Removal, Recycling, Solar Power, HVAC, Energy Efficiency Products, Home Automation
        Leisure & Recreation: Camping, Hiking, Fishing, Picnics, Outdoor Games, Amusement Parks, Swimming, Biking, Rock Climbing, Boating, Kayaking, Sailing, Wildlife Watching, Road Trips
        Technology: Software, Hardware, Gadgets, Cloud Storage, Data Plans, Mobile Devices, Accessories, App Purchases, Subscriptions, Internet Services, Smart Home Devices
        Business Expenses: Office Supplies, Client Meetings, Travel, Subscriptions, Software Licenses, Marketing, Conferences, Trade Shows, Professional Dues, Employee Benefits, Recruiting, Office Rent, Business Insurance
        Social: Parties, Social Events, Networking, Clubs, Dinners, Outings, Gifts for Friends, Group Activities, Community Events, BBQs, Happy Hours
        Outdoor & Adventure: Camping, Fishing, Hunting, Backpacking, Surfing, Rock Climbing, Snowboarding, Kayaking, Diving, Zip Lining, Scuba Diving, Paragliding, Road Trips
        Home Improvement: DIY Projects, Tools, Renovation Materials, Paint, Flooring, Electrical Supplies, Plumbing, Garden Upgrades, Outdoor Furniture, Landscaping, Fencing, Security Systems, Lighting
        Communication: Mobile Plans, Internet Services, Data Plans, Phone Bills, Calling Cards, Fax Services, Messaging Apps, Video Conferencing Subscriptions
        Legal: Attorney Fees, Court Fees, Legal Consultations, Contract Services, Document Processing, Notary Services, Legal Subscriptions, Bail Bonds
        Charity & Donations: Non-Profits, Crowdfunding, Religious Donations, Fundraisers, Charitable Events, Sponsorships, GoFundMe Contributions, Monthly Donations, Volunteering Expenses
        Alcohol & Tobacco: Beer, Wine, Liquor, Cigarettes, Cigars, Vaping, Spirits, Alcohol Delivery, Brewery Tours, Distilleries
        Investment: Stocks, Bonds, Real Estate, Mutual Funds, Cryptocurrencies, Retirement Accounts, Commodities, Crowdfunding Investments, High-Yield Savings Accounts
        Environmental: Solar Panels, Eco-Friendly Products, Sustainable Energy, Recycling Programs, Carbon Offsets, Green Subscriptions, Organic Farming, Renewable Energy Investments
        Religious: Tithes, Religious Offerings, Religious Events, Donations to Religious Organizations, Pilgrimages, Spiritual Retreats, Community Worship Events
        Seasonal: Holiday Gifts, Seasonal Decor, Travel for Holidays, Seasonal Clothing, Seasonal Food, Winter Utilities, Holiday Parties
        Hobbies & Crafts: Sewing, Knitting, Woodworking, Painting, Photography, Pottery, Scrapbooking, Model Building, DIY Kits, Musical Instruments
        Automotive: Car Repairs, Oil Changes, Tires, Vehicle Accessories, Roadside Assistance, Vehicle Maintenance, Car Wash, Detailing
        Maintenance & Repairs: Home Repairs, Vehicle Repairs, Appliance Repairs, Plumbing, Electrical Work, Handyman Services, Roof Repairs, HVAC Maintenance
        Arts & Culture: Museums, Art Galleries, Theatres, Exhibitions, Performances, Cultural Events, Photography, Art Classes, Creative Workshops
        Fashion & Apparel: Clothing, Shoes, Jewelry, Accessories, Designer Brands, Fashion Shows, Tailoring, Seasonal Apparel
        Media & Publications: Magazines, Newspapers, Online Publications, Digital News, E-Books, Audiobooks, Podcasts, Streaming Platforms
        Digital Services: Cloud Storage, Web Hosting, Domain Registration, VPN Services, Antivirus Software, Online Learning Platforms, Graphic Design Tools, Cloud Computing
        Fitness Equipment: Dumbbells, Treadmills, Resistance Bands, Yoga Mats, Fitness Trackers, Home Gym Equipment, Weightlifting Gear, Exercise Bikes
        Wellness & Nutrition: Supplements, Health Foods, Vitamins, Herbal Remedies, Organic Foods, Health Products, Smoothies, Detox Products
        Taxes: Income Taxes, Property Taxes, Self-Employment Taxes, Sales Taxes, Filing Fees, Tax Preparation Services
        Government Fees: Licensing, Permits, Application Fees, Passport Renewal, Visa Applications, Toll Fees, Parking Tickets
        Luxury: High-End Dining, Fine Art, Designer Clothing, Luxury Hotels, VIP Events, Exclusive Clubs, Yachts, Personal Shopping
        Self-care: Therapy, Mental Health Apps, Life Coaching, Meditation Classes, Self-Improvement Books, Wellness Retreats
        DIY & Projects: Woodworking, Gardening, Home Projects, Crafting, Model Building, Restoration Projects

        return everything in smaller case letters
        """

        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": p1},
                ],
                stream=False
            )

            response_text = response.choices[0].message.content.split("\n")

            amount = response_text[0].split(":")[-1].strip()
            recipient = response_text[1].split(":")[-1].strip()
            date_str = response_text[2].split(":")[-1].strip()
            core_category = response_text[3].split(":")[-1].strip()
            sub_category = response_text[4].split(":")[-1].strip()

            self.add_transaction(amount, recipient, date_str, core_category, sub_category, 'SMS')
            self.ids.sms_label.text += f"\nParsed Expense: Amount={amount}, Recipient={recipient}, Date={date_str}, Category={core_category}, Sub-Category={sub_category}"

        except Exception as e:
            self.ids.sms_label.text += f"\nError parsing SMS: {e}"

    def add_transaction(self, amount, recipient, date, core_category, sub_category, source, location=None):
        data = {
                'amount': amount,
                'core_category': core_category,
                'sub_category': sub_category,
                'recipient': recipient,
                'date': date,
                'source': source,
                'location': location
            }
        db.child("transactions").push(data)

        print(f"Transaction added to Firestore: Amount={amount}, Recipient={recipient}")

class BillScreen(Screen):
    pass

class VoiceScreen(Screen):
    pass

class MultilingualVoiceScreen(Screen):
    pass

class QueryBotScreen(Screen):
    pass

class ScreenManagement(ScreenManager):
    pass

class ExpenseTrackerApp(App):
    def build(self):
        return Builder.load_file("main.kv")

if __name__ == "__main__":
    ExpenseTrackerApp().run()