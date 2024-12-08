from .models import Auction, AuctionPicture, AuctionVideo, Favourite, Bid
from .forms import AuctionForm, AuctionPictureForm, AuctionVideoForm
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .forms import BidForm  # Import the BidForm
from datetime import datetime
from django.utils import timezone
from datetime import timedelta
from .forms import AuctionFilterForm
from django.db.models import Q
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from django.http import JsonResponse


def home(request):
    return render(request, 'home.html')




def auction_list(request):
    selected_category = request.GET.get('category', '')
    order_by = request.GET.get('order_by','')
    list_option = request.GET.get('list_option', '')
    form = AuctionFilterForm(request.GET or None)
    auctions = Auction.objects.all()
    auctions = auctions.order_by('-start_date')


    if list_option == 'open':
        auctions = auctions.filter(end_date__gt=timezone.now())
    elif list_option == 'favourite':
        if request.user.is_authenticated:
            favourites = set(Favourite.objects.filter(user=request.user).values_list('auction_id', flat=True))
            auctions = auctions.filter(id__in=favourites)
        else:
            messages.error(request, 'You need to log in to display your favourites.')
            return redirect('login')
    elif list_option == 'closed':
        auctions = auctions.filter(end_date__lt=timezone.now())
    elif list_option == 'my_auctions':
        if request.user.is_authenticated:
            auctions = auctions.filter(seller=request.user)
        else:
            messages.error(request, 'You need to log in to display your auctions.')
            return redirect('login')



    if form.is_valid():
        #print("The form is valid : ")
        category = form.cleaned_data.get('category')
        #print(" Category : ", category)
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        min_bid = form.cleaned_data.get('min_bid')
        order_by = form.cleaned_data.get('order_by')

        if category and category != "All":
            auctions = auctions.filter(category__icontains=category)
        
        if start_date: 
            auctions=auctions.filter(start_date__gte=start_date)
        if end_date: 
            auctions=auctions.filter(end_date__lte=end_date+timedelta(days=1))
        
        
        if min_bid is not None:
            auctions = auctions.filter(
                Q(current_bid__gte=min_bid) | 
                Q(current_bid__isnull=True) & Q(initial_price__gte=min_bid)
            )
    else:
        print("Form errors: ", form.errors)


    # Apply sorting
    if order_by == 'recent':
        auctions = auctions.order_by('-start_date')
    elif order_by == 'end_date':
        auctions = auctions.order_by('end_date')
    elif order_by == 'highest_bids':
        auctions = auctions.order_by('-current_bid')

        # Pagination
    paginator = Paginator(auctions, 9)  # Show 5 auctions per page
    print("Paginator : ", paginator)
    page = request.GET.get('page')
    
    try:
        paginated_auctions = paginator.page(page)
    except PageNotAnInteger:
        paginated_auctions = paginator.page(1)
    except EmptyPage:
        paginated_auctions = paginator.page(paginator.num_pages)


    auction_data = []
    
    user = request.user if request.user.is_authenticated else None
    favourites = set()

    if user:
        favourites = set(Favourite.objects.filter(user=user).values_list('auction_id', flat=True))

    


    for auction in paginated_auctions:
        first_image = AuctionPicture.objects.filter(auction=auction).first()
        image_url = first_image.image.url if first_image else '/static/images/default-image.png'
        auction_data.append({
            'auction': auction,
            'image_url': image_url,
            'is_favourite': auction.id in favourites,  # Check if the auction is a favourite
        })

    


    current_time=timezone.now()
    
    

    return render(request, 'auction_list.html', {
        'auction_data': auction_data,
        'form': form,
        'selected_category': selected_category,
        'current_time':current_time,
        'page_obj': paginated_auctions,  # Pass the paginated auctions to the template
        'list_option': list_option,  # Pass the list option to the template
    })


######################################################################################################################################

def open_auctions_list(request):
    
    
    selected_category = request.GET.get('category', '')
    order_by = request.GET.get('order_by','')
    form = AuctionFilterForm(request.GET or None)
    auctions = Auction.objects.all()

    auctions = auctions.filter(end_date__gt=timezone.now())

    if form.is_valid():
        print("The form is valid : ")
        category = form.cleaned_data.get('category')
        #print(" Category : ", category)
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        min_bid = form.cleaned_data.get('min_bid')
        order_by = form.cleaned_data.get('order_by')

        if category and category != "All":
            auctions = auctions.filter(category__icontains=category)
        
        if start_date: 
            auctions=auctions.filter(start_date__gte=start_date)
        if end_date: 
            auctions=auctions.filter(end_date__lte=end_date+timedelta(days=1))
        
        
        if min_bid is not None:
            auctions = auctions.filter(
                Q(current_bid__gte=min_bid) | 
                Q(current_bid__isnull=True) & Q(initial_price__gte=min_bid)
            )
    else:
        print("Form errors: ", form.errors)


    auctions = auctions.order_by('-start_date')

    # Apply sorting
    if order_by == 'recent':
        auctions = auctions.order_by('-start_date')
    elif order_by == 'end_date':
        auctions = auctions.order_by('end_date')
    elif order_by == 'highest_bids':
        auctions = auctions.order_by('-current_bid')

    # Pagination
    paginator = Paginator(auctions, 9)  # Show 5 auctions per page
    page = request.GET.get('page')
    
    try:
        paginated_auctions = paginator.page(page)
    except PageNotAnInteger:
        paginated_auctions = paginator.page(1)
    except EmptyPage:
        paginated_auctions = paginator.page(paginator.num_pages)


    auction_data = []
    for auction in paginated_auctions:
        first_image = AuctionPicture.objects.filter(auction=auction).first()
        image_url = first_image.image.url if first_image else '/static/images/default-image.png'
        auction_data.append({
            'auction': auction,
            'image_url': image_url,
        })

    current_time=timezone.now()

    return render(request, 'auction_list.html', {
            'auction_data': auction_data,
            'open_auctions':True,
            'form': form,
            'selected_category': selected_category,
            'current_time':current_time,
            'page_obj': paginated_auctions,  # Pass the paginated auctions to the template
            
            })





#@login_required
def auction_detail(request, pk):
    auction = get_object_or_404(Auction, pk=pk)
    bid_form = BidForm()
    current_time=timezone.now()
    # Calculate the minimum required bid
    if auction.current_bid:
        current_bid=auction.current_bid
    else:
        current_bid=auction.initial_price
    minimum_required_bid = calculate_minimum_bid(current_bid)
    step=min_increment(current_bid)

    user = request.user if request.user.is_authenticated else None
    is_favourite = False

    if user:
        favourites = set(Favourite.objects.filter(user=user).values_list('auction_id', flat=True))
        is_favourite = auction.id in favourites
        print("Debugging : ", is_favourite)



    bids = Bid.objects.filter(auction=auction).order_by('-amount')

    # Prepare bid data for Chart.js
    bid_labels = [bid.timestamp.strftime('%c') for bid in bids]  # Access 'date' as an attribute and format it
    bid_amounts = [float(bid.amount) for bid in bids]  # Access 'amount' as an attribute
    user_names = [bid.user.username for bid in bids]  # Access 'username' through the related 'user'
    user_avatars = [bid.user.avatar.url if bid.user.avatar else 'default_avatar_url' for bid in bids]  # Access avatar properly






    return render(request, 'auction_detail.html', {
        'auction': auction,
        'bid_form': bid_form,
        'current_time': current_time,
        'minimum_required_bid':minimum_required_bid,
        'step':step,
        'is_favourite': is_favourite,
        'bids': bids,
        'bid_labels': bid_labels,
        'bid_amounts': bid_amounts,
        'user_names': user_names,
        'user_avatars': user_avatars,
    })

#@login_required
def submit_bid(request, pk):
    auction = get_object_or_404(Auction, pk=pk)

    # Check if user is authenticated
    if not request.user.is_authenticated:
        messages.error(request, 'You need to log in to place a bid.')
        return redirect('login')
    

    bid_form = BidForm(request.POST)

    # Check if the current date and time are before the auction's end date
    if timezone.now() > auction.end_date:
        messages.error(request, 'The auction has ended. You cannot place a bid.')
        return redirect('auction_detail', pk=pk)

    if bid_form.is_valid():
        bid_amount = bid_form.cleaned_data['bid_amount']


        # Handle None values by defaulting to 0
        current_bid = auction.current_bid or 0
        initial_price = auction.initial_price or 0


        # Convert values to float for comparison
        bid_amount = float(bid_amount)
        current_bid = float(current_bid)
        initial_price = float(initial_price)
       

        # Calculate the minimum required bid
        if auction.current_bid:
            current_bid=auction.current_bid
        else:
            current_bid=auction.initial_price
        minimum_required_bid = calculate_minimum_bid(current_bid)
        minimum_required_bid = float(minimum_required_bid)
    

        # Check if the bid is higher than the current bid
        if bid_amount >= minimum_required_bid and bid_amount > initial_price:
            auction.current_bid = bid_amount
            auction.current_bidder = request.user
            auction.save()

            # **Create a new Bid entry**
            Bid.objects.create(
                auction=auction,
                user=request.user,
                amount=bid_amount
            )

            send_auction_update(auction.pk, bid_amount, request.user.username,request.user.avatar.url)
            '''
             # Send a WebSocket message
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'auction_{pk}',
                {
                    'type': 'auction_update',  # Update to 'auction_update' or match consumer type
                    'bid_amount': bid_amount,
                    'bidder': request.user.username,
                }
            )
            ''' 

            # Success message
            messages.success(request, 'Your bid is successfuly accepted !')
            return redirect('auction_detail', pk=pk)
        else:
            # Handle bid error (optional: return an error message)
            #bid_form.add_error('bid_amount', f'Your bid must be at least ${minimum_required_bid:.2f}.')
            messages.error(request, f'Your bid must be at least {minimum_required_bid:.2f}.')
            return redirect('auction_detail', pk=pk)
    
    
    current_time=timezone.now()

    return render(request, 'auction_detail.html', {
        'auction': auction,
        'bid_form': bid_form,
        'current_time':current_time,
        'minimum_required_bid':minimum_required_bid,
        
    })



def send_auction_update(auction_id, bid_amount, bidder,avatar_url):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'auction_{auction_id}',
        {
            'type': 'auction_update',
            'current_bid': bid_amount,
            'current_bidder': bidder,
            'avatar_url':avatar_url,
        }
    )


def add_auction(request):

    # Check if user is authenticated
    if not request.user.is_authenticated:
        messages.error(request, 'You need to log in to place a bid.')
        return redirect('login')
    

    if request.method == 'POST':
        auction_form = AuctionForm(request.POST, request.FILES)
        video_form = AuctionVideoForm(request.POST)

        if auction_form.is_valid() and video_form.is_valid():
            auction = auction_form.save(commit=False)
            auction.seller = request.user
            auction.save()

            # Handle the main picture
            if 'image' in request.FILES:
                main_picture = request.FILES['image']
                AuctionPicture.objects.create(auction=auction, image=main_picture)

            # Handle additional pictures
            for key in request.FILES:
                if key.startswith('image_'):
                    picture = request.FILES[key]
                    AuctionPicture.objects.create(auction=auction, image=picture)

            # Handle video
            video = video_form.save(commit=False)
            video.auction = auction
            video.save()

            # Success message
            messages.success(request, 'Your Auction is successfully submitted !')
            print("coordinates passed: ", auction.location_latitude , ", ", auction.location_longitude)

            return redirect('auction_list')
    else:
        auction_form = AuctionForm()
        video_form = AuctionVideoForm()

    
    return render(request, 'add_auction.html', {
        'auction_form': auction_form,
        'video_form': video_form,
    })







#@login_required
def my_auctions(request):

    # Check if user is authenticated
    if not request.user.is_authenticated:
        messages.error(request, 'You need to log in to display your auctions.')
        return redirect('login')
    

    user = request.user
    
    
    selected_category = request.GET.get('category', '')
    order_by = request.GET.get('order_by','')
    form = AuctionFilterForm(request.GET or None)
    auctions = Auction.objects.all()

    auctions = auctions.filter(seller=user)

    if form.is_valid():
        #print("The form is valid : ")
        category = form.cleaned_data.get('category')
        #print(" Category : ", category)
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        min_bid = form.cleaned_data.get('min_bid')
        order_by = form.cleaned_data.get('order_by')

        if category and category != "All":
            auctions = auctions.filter(category__icontains=category)
        if start_date: 
            auctions=auctions.filter(start_date__gte=start_date)
        if end_date: 
            auctions=auctions.filter(end_date__lte=end_date+timedelta(days=1))
        
        
        if min_bid is not None:
            auctions = auctions.filter(
                Q(current_bid__gte=min_bid) | 
                Q(current_bid__isnull=True) & Q(initial_price__gte=min_bid)
            )
    else:
        print("Form errors: ", form.errors)


    # Apply sorting
    if order_by == 'recent':
        auctions = auctions.order_by('-start_date')
    elif order_by == 'end_date':
        auctions = auctions.order_by('end_date')
    elif order_by == 'highest_bids':
        auctions = auctions.order_by('-current_bid')
    # Pagination
    paginator = Paginator(auctions, 9)  # Show 9 auctions per page
    page = request.GET.get('page')
    
    try:
        paginated_auctions = paginator.page(page)
    except PageNotAnInteger:
        paginated_auctions = paginator.page(1)
    except EmptyPage:
        paginated_auctions = paginator.page(paginator.num_pages)


    auction_data = []
    for auction in paginated_auctions:
        first_image = AuctionPicture.objects.filter(auction=auction).first()
        image_url = first_image.image.url if first_image else '/static/images/default-image.png'
        auction_data.append({
            'auction': auction,
            'image_url': image_url,
        })
    
    return render(request, 'auction_list.html', {
        'auction_data': auction_data,
        'my_auctions': True,
        'form': form,
        'selected_category': selected_category,
        'page_obj': paginated_auctions,  # Pass the paginated auctions to the template

    })



def about_us(request):
    return render(request, 'about_us.html')


def contact_us(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        # Construct the email message
        full_message = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"

        try:
            # Send the email
            send_mail(
                subject=f"Contact Us: {subject}",
                message=full_message,
                from_email=email,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],
            )
            # Success message
            messages.success(request, 'Thank you for contacting us! We will get back to you soon.')
            return redirect('contact_us')
        except Exception as e:
            # Error message
            messages.error(request, f'Sorry, something went wrong. Please try again later. Error: {str(e)}')
            return redirect('contact_us')

    return render(request, 'contact_us.html')


 # Define bid increment logic
def calculate_minimum_bid(current_bid):
    
    return min_increment(current_bid)+current_bid
    
def min_increment(current_bid):
    if current_bid <= 1000:
        return  10
    elif current_bid <= 5000:
        return  50
    elif current_bid <= 10000:
        return  100
    elif current_bid <= 50000:
        return  500
    else:
        return  1000
    



@login_required
def toggle_favourite(request, auction_id):
    print("Toggle_favourite view funtion is called  ")
    auction = get_object_or_404(Auction, id=auction_id)
    if Favourite.objects.filter(user=request.user, auction=auction).exists():
        Favourite.objects.filter(user=request.user, auction=auction).delete()
        action = 'removed'
    else:
        Favourite.objects.create(user=request.user, auction=auction)
        action = 'added'
    
    print ("The action is : favourate is ", action)
    return JsonResponse({'success': True, 'action': action})