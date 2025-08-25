import os
from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, send_file, abort, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy import or_
from app import app, db
from models import User, Book, Category, Download
from forms import (LoginForm, UserForm, EditUserForm, ChangePasswordForm, 
                  CategoryForm, BookForm, EditBookForm, SearchForm)

@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('user_dashboard'))
    
    # Show recent books for non-authenticated users
    recent_books = Book.query.order_by(Book.uploaded_at.desc()).limit(6).all()
    categories = Category.query.all()
    return render_template('index.html', recent_books=recent_books, categories=categories)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            user.last_login = datetime.utcnow()
            db.session.commit()
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('index')
            flash(f'Welcome back, {user.full_name}!', 'success')
            return redirect(next_page)
        flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# Admin Routes
@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    total_books = Book.query.count()
    total_users = User.query.filter_by(is_admin=False).count()
    total_downloads = Download.query.count()
    recent_downloads = Download.query.order_by(Download.downloaded_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                         total_books=total_books,
                         total_users=total_users, 
                         total_downloads=total_downloads,
                         recent_downloads=recent_downloads)

@app.route('/admin/books')
@login_required
def admin_books():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    page = request.args.get('page', 1, type=int)
    books = Book.query.order_by(Book.uploaded_at.desc()).paginate(
        page=page, per_page=10, error_out=False)
    return render_template('admin/books.html', books=books)

@app.route('/admin/books/add', methods=['GET', 'POST'])
@login_required
def admin_add_book():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    form = BookForm()
    if form.validate_on_submit():
        file = form.file.data
        filename = secure_filename(file.filename)
        
        # Ensure uploads directory exists
        upload_dir = os.path.join(os.getcwd(), 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Create full file path
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
        
        book = Book(
            title=form.title.data,
            author=form.author.data,
            description=form.description.data,
            category_id=form.category_id.data,
            filename=filename,
            file_path=file_path,
            file_size=os.path.getsize(file_path),
            uploaded_by=current_user.id
        )
        db.session.add(book)
        db.session.commit()
        flash('Book uploaded successfully!', 'success')
        return redirect(url_for('admin_books'))
    
    return render_template('admin/add_book.html', form=form)

@app.route('/admin/books/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_edit_book(id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    book = Book.query.get_or_404(id)
    form = EditBookForm(obj=book)
    
    if form.validate_on_submit():
        book.title = form.title.data
        book.author = form.author.data
        book.description = form.description.data
        book.category_id = form.category_id.data
        db.session.commit()
        flash('Book updated successfully!', 'success')
        return redirect(url_for('admin_books'))
    
    return render_template('admin/edit_book.html', form=form, book=book)

@app.route('/admin/books/delete/<int:id>')
@login_required
def admin_delete_book(id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    book = Book.query.get_or_404(id)
    
    # Delete file from filesystem
    try:
        # Ensure the file path is absolute
        if not os.path.isabs(book.file_path):
            file_path = os.path.join(os.getcwd(), book.file_path)
        else:
            file_path = book.file_path
            
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        current_app.logger.error(f"Error deleting file {file_path}: {e}")
    
    db.session.delete(book)
    db.session.commit()
    flash('Book deleted successfully!', 'success')
    return redirect(url_for('admin_books'))

@app.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    users = User.query.filter_by(is_admin=False).order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/users/add', methods=['GET', 'POST'])
@login_required
def admin_add_user():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    form = UserForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            full_name=form.full_name.data,
            is_admin=form.is_admin.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('User created successfully!', 'success')
        return redirect(url_for('admin_users'))
    
    return render_template('admin/add_user.html', form=form)

@app.route('/admin/users/delete/<int:id>')
@login_required
def admin_delete_user(id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(id)
    if user.is_admin:
        flash('Cannot delete admin users.', 'danger')
        return redirect(url_for('admin_users'))
    
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/downloads')
@login_required
def admin_downloads():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    page = request.args.get('page', 1, type=int)
    downloads = Download.query.order_by(Download.downloaded_at.desc()).paginate(
        page=page, per_page=20, error_out=False)
    return render_template('admin/downloads.html', downloads=downloads)

@app.route('/admin/categories', methods=['GET', 'POST'])
@login_required
def admin_categories():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(
            name=form.name.data,
            description=form.description.data
        )
        db.session.add(category)
        db.session.commit()
        flash('Category created successfully!', 'success')
        return redirect(url_for('admin_categories'))
    
    categories = Category.query.order_by(Category.name).all()
    return render_template('admin/categories.html', form=form, categories=categories)

@app.route('/admin/categories/delete/<int:id>')
@login_required
def admin_delete_category(id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    category = Category.query.get_or_404(id)
    
    # Check if category has books
    if len(category.books) > 0:
        flash('Cannot delete category that contains books. Please move or delete the books first.', 'danger')
        return redirect(url_for('admin_categories'))
    
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted successfully!', 'success')
    return redirect(url_for('admin_categories'))

# User Routes
@app.route('/dashboard')
@login_required
def user_dashboard():
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    
    recent_books = Book.query.order_by(Book.uploaded_at.desc()).limit(6).all()
    user_downloads = Download.query.filter_by(user_id=current_user.id).count()
    return render_template('user/dashboard.html', 
                         recent_books=recent_books, 
                         user_downloads=user_downloads)

@app.route('/books')
def books():
    form = SearchForm()
    page = request.args.get('page', 1, type=int)
    query = request.args.get('query', '')
    category_id = request.args.get('category', 0, type=int)
    
    books_query = Book.query
    
    if query:
        books_query = books_query.filter(
            or_(Book.title.contains(query), Book.author.contains(query))
        )
    
    if category_id:
        books_query = books_query.filter_by(category_id=category_id)
    
    books = books_query.order_by(Book.uploaded_at.desc()).paginate(
        page=page, per_page=12, error_out=False)
    
    categories = Category.query.all()
    return render_template('user/books.html', 
                         books=books, 
                         form=form, 
                         categories=categories,
                         query=query,
                         selected_category=category_id)

@app.route('/download/<int:book_id>')
@login_required
def download_book(book_id):
    book = Book.query.get_or_404(book_id)
    
    # Record download
    download = Download(
        user_id=current_user.id,
        book_id=book.id,
        ip_address=request.remote_addr
    )
    db.session.add(download)
    db.session.commit()
    
    try:
        # Ensure the file path is absolute
        if not os.path.isabs(book.file_path):
            file_path = os.path.join(os.getcwd(), book.file_path)
        else:
            file_path = book.file_path
            
        return send_file(file_path, as_attachment=True, download_name=book.filename)
    except FileNotFoundError:
        flash('File not found. Please contact administrator.', 'danger')
        return redirect(url_for('books'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if current_user.is_admin:
        flash('Admins cannot edit profile here. Please contact system administrator.', 'info')
        return redirect(url_for('admin_dashboard'))
    
    form = EditUserForm(obj=current_user)
    password_form = ChangePasswordForm()
    
    if form.validate_on_submit() and 'update_profile' in request.form:
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.full_name = form.full_name.data
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    if password_form.validate_on_submit() and 'change_password' in request.form:
        if current_user.check_password(password_form.current_password.data):
            current_user.set_password(password_form.password.data)
            db.session.commit()
            flash('Password changed successfully!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Current password is incorrect.', 'danger')
    
    user_downloads = Download.query.filter_by(user_id=current_user.id).order_by(
        Download.downloaded_at.desc()).limit(10).all()
    
    return render_template('user/profile.html', 
                         form=form, 
                         password_form=password_form,
                         user_downloads=user_downloads)

# Initialize default categories (moved to app.py)
