from .models import Stock, Portfolio, DailyWorth, Profile
from yahoo_fin import stock_info as si


def update_daily_net_worth():
    # Update stock price 30 mins after stock markets closes at 4 p.m. Eastern Standard Time (EST) in the U.S
    all_profiles = Profile.objects.get()
    for profile in all_profiles:
        username = profile.user

        user_portfolios = Portfolio.objects.get(user = username)
        if not user_portfolios:
            pass
        else:
            total_worth = 0
            for port in user_portfolios: 
                price = si.get_live_price(port.stock)
                total_worth += price * port.number
            daily_worth_to_update = DailyWorth.objects.get(user = username)
            daily_worth_to_update = total_worth
            daily_worth_to_update.save()
    
        
            


