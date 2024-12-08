# tasks.py

from django.core.mail import send_mail
from django.utils import timezone
from .models import Auction
from celery import shared_task


@shared_task
def check_and_send_winner_emails():
    now = timezone.now()
    auctions = Auction.objects.filter(end_date__lt=now, winner_email_sent=False)
    
    for auction in auctions:

        seller_email = auction.seller.email

        if auction.current_bidder:  # Ensure there is a current bidder
            # Get the email of the current bidder
            winner_email = auction.current_bidder.email
            print(" Congratulations Email to be sent to : "+winner_email)


            # Send email to the winner
            subject = 'Congratulations! You Have Won the Auction'
            message = (
                f'Hello {auction.current_bidder.username},\n\n'
                f'Congratulations! You have won the auction for "{auction.title}".\n\n'
                f'Auction Details:\n'
                f'Title: {auction.title}\n'
                f'Category: {auction.category}\n'
                f'Description: {auction.description}\n'
                f'Start Date: {auction.start_date.strftime("%Y-%m-%d %H:%M:%S")}\n'
                f'End Date: {auction.end_date.strftime("%Y-%m-%d %H:%M:%S")}\n'
                f'Final Bid Amount: ${auction.current_bid}\n\n'
                f'Please contact the seller for further instructions on completing the transaction.\n\n'
                f'Thank you for participating in our auction!\n'
                f'Best regards,\n'
                f'The Auction Site Team'
            )
            
            # Send email to the winner
            send_mail(
                subject,
                message,
                'emineazaiez@live.fr',
                [winner_email],
                fail_silently=False,
            )

            print(" Congratulations Email to be sent to the seller : "+seller_email)

            # Prepare the email to the seller
            subject_seller = 'Auction Closed - Winning Bid Information'
            message_seller = (
                f'Hello {auction.seller.username},\n\n'
                f'The auction for "{auction.title}" has closed.\n\n'
                f'Auction Details:\n'
                f'Title: {auction.title}\n'
                f'Category: {auction.category}\n'
                f'Description: {auction.description}\n'
                f'Start Date: {auction.start_date.strftime("%Y-%m-%d %H:%M:%S")}\n'
                f'End Date: {auction.end_date.strftime("%Y-%m-%d %H:%M:%S")}\n'
                f'Winning Bid Amount: ${auction.current_bid}\n\n'
                f'Winning Bidder Details:\n'
                f'Name: {auction.current_bidder.username}\n'
                f'Email: {auction.current_bidder.email}\n\n'
                f'Please reach out to the winning bidder to complete the transaction.\n\n'
                f'Thank you for using our auction platform!\n'
                f'Best regards,\n'
                f'The Auction Site Team'
            )

            # Send email to the seller
            send_mail(
                subject_seller,
                message_seller,
                'emineazaiez@live.fr',
                [seller_email],
                fail_silently=False,
            )

            # Mark the email as sent
            auction.winner_email_sent = True
            auction.save()

        else:
            # Log or handle the case where there is no current bidder
            print(f'No bidder for 1the auction {auction.id}')
            # Prepare the email to the seller when there is no current bidder
            subject_no_bidder = 'Auction Closed - No Bids Received'
            message_no_bidder = (
                f'Hello {auction.seller.username},\n\n'
                f'The auction for "{auction.title}" has closed, but unfortunately, no bids were received.\n\n'
                f'Auction Details:\n'
                f'Title: {auction.title}\n'
                f'Category: {auction.category}\n'
                f'Description: {auction.description}\n'
                f'Start Date: {auction.start_date.strftime("%Y-%m-%d %H:%M:%S")}\n'
                f'End Date: {auction.end_date.strftime("%Y-%m-%d %H:%M:%S")}\n\n'
                f'Since no bids were placed, there is no winner for this auction.\n\n'
                f'If you have any questions or need further assistance, please contact us.\n\n'
                f'Thank you for using our auction platform!\n'
                f'Best regards,\n'
                f'The Auction Site Team'
            )

            # Send email to the seller
            send_mail(
                subject_no_bidder,
                message_no_bidder,
                'emineazaiez@live.fr',
                [seller_email],
                fail_silently=False,
            )
            print("Email to seller that the auction is not sold is sent")
            
            # Mark the email as sent
            auction.winner_email_sent = True
            auction.save()