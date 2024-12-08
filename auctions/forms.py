# forms.py

from django import forms
from .models import Auction, AuctionPicture, AuctionVideo

class AuctionForm(forms.ModelForm):
    class Meta:
        model = Auction
        fields = ['title', 'category', 'description', 'start_date', 'end_date', 'initial_price', 'reveal_identity', 'legal_responsibility', 'location_latitude', 'location_longitude']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'initial_price': forms.TextInput(attrs={'class': 'form-control'}),
            'reveal_identity': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'legal_responsibility': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'location_latitude': forms.HiddenInput(),  # Hidden field for latitude
            'location_longitude': forms.HiddenInput(),  # Hidden field for longitude
        }

class AuctionPictureForm(forms.ModelForm):
    class Meta:
        model = AuctionPicture
        fields = ['image']

class AuctionVideoForm(forms.ModelForm):
    class Meta:
        model = AuctionVideo
        fields = ['video_url']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make the video_url field optional
        self.fields['video_url'].required = False




class BidForm(forms.Form):
    bid_amount = forms.DecimalField(decimal_places=2, max_digits=10, label='Your Bid')




class AuctionFilterForm(forms.Form):
    category = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'id': 'id_category', 'class': 'form-control'})
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    min_bid = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    ORDER_CHOICES = [
        ('recent', 'Recent'),
        ('end_date', 'Closest End Date'),
        ('highest_bids', 'Highest bids'),
        # Add more order choices as needed
    ]
    
    order_by = forms.ChoiceField(choices=ORDER_CHOICES, required=False)