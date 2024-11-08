from django.shortcuts import render, HttpResponse, redirect, get_object_or_404, redirect
from .models import Product, Transaction
from django.contrib.auth.decorators import login_required
from .forms import ProductForm

from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm

from .models import SoldItem, BoughtItem
from django.contrib import messages

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # Get the authenticated user
            user = form.get_user()
            login(request, user)  # Log the user in
            return redirect('home')  # Redirect to home page after login
        else:
            messages.error(request, 'Invalid username or password')  # Display error message
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})  # Render login page with form


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import UserProfile, SoldItem, BoughtItem
from .forms import UserProfileForm

@login_required
def profile_view(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user_profile)

    sold_items = SoldItem.objects.filter(seller=user_profile)
    bought_items = BoughtItem.objects.filter(buyer=user_profile)

    return render(request, 'profile.html', {
        'form': form,
        'user_profile': user_profile,
        'sold_items': sold_items,
        'bought_items': bought_items,
    })



@login_required
def index(request):
    context = {}
    return render(request , 'index.html' , context)

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile
from .forms import UserProfileForm

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import CustomUserCreationForm
from .forms import UserProfileForm


def register(request):
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()  # Save the user and email
            profile = profile_form.save(commit=False)
            profile.user = user  # Link profile to the user
            profile.wallet_balance = 0.00  # Set default wallet balance
            profile.save()  # Save the profile

            return redirect('login')

    else:
        user_form = CustomUserCreationForm()
        profile_form = UserProfileForm()

    return render(request, 'register.html', {'user_form': user_form, 'profile_form': profile_form})




@login_required
def product_list(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})







from django.shortcuts import render, get_object_or_404
from .models import Product, Transaction, UserProfile


@login_required
def product_detail(request, pk):  # Use 'pk' here
    product = get_object_or_404(Product, id=pk)  # Fetch the product by 'pk'
    user_profile = request.user.userprofile  # Assuming user has a linked UserProfile
    
    # Check if a transaction already exists, otherwise create a new one
    transaction, created = Transaction.objects.get_or_create(
        buyer=user_profile,
        product=product,
        defaults={'seller': product.seller, 'amount': product.price, 'confirmed': False}
    )

    context = {
        'product': product,
        'transaction': transaction,
    }
    return render(request, 'product_detail.html', context)


from django.shortcuts import render, redirect
from .forms import ProductForm

from django.shortcuts import render, redirect
from .models import Product, UserProfile
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Product, UserProfile
from django.core.exceptions import ObjectDoesNotExist

@login_required
def sell_product(request):
    if request.method == 'POST':
        product_name = request.POST.get('name')
        product_description = request.POST.get('description')  # Capture description
        product_price = request.POST.get('price')
        product_category = request.POST.get('category')  # Capture category
        product_image = request.FILES.get('image')  # Capture the uploaded image

        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return render(request, 'error.html', {'message': 'UserProfile does not exist for this user.'})

        # Create a new Product instance
        product = Product(
            name=product_name,
            description=product_description,  # Save the description
            price=product_price,
            category=product_category,  # Save the category
            seller=user_profile,
            image=product_image  # Save the image
        )
        product.save()  # Save the Product instance
        return redirect('product_list')  # Redirect after saving

    return render(request, 'sell_product.html')  # Render the form for selling


from django.shortcuts import render

def rate_limited(request):
    return render(request, 'rate_limited.html', status=429)  # HTTP 429 Too Many Requests



from django.shortcuts import render, get_object_or_404, redirect
from django.db import transaction
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import UserProfile, Transaction, Product, SoldItem, BoughtItem


@login_required
@transaction.atomic
def confirm_transaction(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    buyer = request.user.userprofile  # Logged-in user
    seller = product.seller  # Seller of the product

    if request.method == 'POST':
        amount = product.price  # Transaction amount is the product's price

        # Check if the buyer has enough balance
        if buyer.wallet_balance < amount:
            messages.error(request, "Insufficient funds in your wallet.")
            return redirect('product_detail', pk=product.id)

        # Deduct the amount from buyer's wallet
        buyer.wallet_balance -= amount
        buyer.save()

        seller.wallet_balance += amount
        seller.save()

        # Create SoldItem and BoughtItem records with PIDs
        SoldItem.objects.create(
            seller=seller,
            name=product.name,
            price=amount,
            buyer_pid=buyer.pid  # Save buyer's PID
        )
        BoughtItem.objects.create(
            buyer=buyer,
            name=product.name,
            price=amount,
            seller_pid=seller.pid  # Save seller's PID
        )

        # Create a Transaction record upon confirmation
        transaction = Transaction.objects.create(
            buyer=buyer,
            seller=seller,
            product=product,
            amount=amount,
            confirmed=True
        )

        # Optionally, mark the product as sold instead of deleting it
        product.delete()  # Removes the product completely

        messages.success(request, "Transaction completed successfully.")
        return redirect('product_list')  # Redirect to product list or another appropriate page

    # For GET request, render the confirmation page
    context = {
        'product': product,
        'buyer': buyer,
        'seller': seller,
        'amount': product.price,
    }
    return render(request, 'confirm_transaction.html', context)





from django.shortcuts import render, get_object_or_404, redirect
from django.db import transaction as db_transaction
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import UserProfile, Transaction, Product, SoldItem, BoughtItem

@login_required
def buy_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    buyer = request.user.userprofile  # Assuming there's a UserProfile related to the user
    seller = product.seller  # Assuming 'seller' is a field in the Product model

    # Check if the buyer is trying to buy their own product
    if buyer.pid == seller.pid:
        # Set an error message and return to the product detail page
        messages.error(request, "You cannot buy a product that you published for selling.")
        return redirect('product_detail', pk=pk)

    if request.method == 'POST':
        # Redirect to the confirmation page without creating a transaction
        return redirect('confirm_transaction', product_id=product.id)

    # If not a POST request, redirect back to product detail
    return redirect('product_detail', pk=pk)



