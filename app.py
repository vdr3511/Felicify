from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get('SECRET_KEY', 'devkey')
db = SQLAlchemy(app)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    done = db.Column(db.Boolean, default=False)
    due_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Task {self.title}>"


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Expense {self.description} {self.amount}>"


class ShoppingItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    qty = db.Column(db.String(50), nullable=True)
    bought = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<Item {self.name}>"


class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(120), nullable=True)

    def __repr__(self):
        return f"<Member {self.name}>"


def create_tables():
    # Ensure tables exist. Some Flask versions may not provide
    # the `before_first_request` decorator as an attribute on the
    # app object in certain runtime configurations, so call this
    # explicitly from the main block using an app context.
    db.create_all()


@app.route('/')
def index():
    tasks = Task.query.order_by(Task.created_at.desc()).limit(5).all()
    expenses = Expense.query.order_by(Expense.created_at.desc()).limit(5).all()
    items = ShoppingItem.query.order_by(ShoppingItem.id.desc()).limit(6).all()
    members = Member.query.all()
    total_expenses = db.session.query(db.func.sum(Expense.amount)).scalar() or 0
    return render_template('index.html', tasks=tasks, expenses=expenses, items=items, members=members, total_expenses=total_expenses)


@app.route('/tasks', methods=['GET', 'POST'])
def tasks_view():
    if request.method == 'POST':
        title = request.form.get('title')
        notes = request.form.get('notes')
        due = request.form.get('due_date')
        due_dt = datetime.fromisoformat(due) if due else None
        if not title:
            flash('Task title required', 'danger')
        else:
            t = Task(title=title, notes=notes, due_date=due_dt)
            db.session.add(t)
            db.session.commit()
            flash('Task added', 'success')
        return redirect(url_for('tasks_view'))
    tasks = Task.query.order_by(Task.created_at.desc()).all()
    return render_template('tasks.html', tasks=tasks)


@app.route('/tasks/<int:task_id>/toggle')
def toggle_task(task_id):
    t = Task.query.get_or_404(task_id)
    t.done = not t.done
    db.session.commit()
    return redirect(request.referrer or url_for('tasks_view'))


@app.route('/tasks/<int:task_id>/delete')
def delete_task(task_id):
    t = Task.query.get_or_404(task_id)
    db.session.delete(t)
    db.session.commit()
    flash('Task removed', 'info')
    return redirect(request.referrer or url_for('tasks_view'))


@app.route('/expenses', methods=['GET', 'POST'])
def expenses_view():
    if request.method == 'POST':
        desc = request.form.get('description')
        amount = request.form.get('amount')
        category = request.form.get('category')
        try:
            amt = float(amount)
        except (ValueError, TypeError):
            flash('Invalid amount', 'danger')
            return redirect(url_for('expenses_view'))
        e = Expense(description=desc, amount=amt, category=category)
        db.session.add(e)
        db.session.commit()
        flash('Expense recorded', 'success')
        return redirect(url_for('expenses_view'))
    expenses = Expense.query.order_by(Expense.created_at.desc()).all()
    total = db.session.query(db.func.sum(Expense.amount)).scalar() or 0
    return render_template('expenses.html', expenses=expenses, total=total)


@app.route('/shopping', methods=['GET', 'POST'])
def shopping_view():
    if request.method == 'POST':
        name = request.form.get('name')
        qty = request.form.get('qty')
        if not name:
            flash('Provide an item name', 'danger')
        else:
            it = ShoppingItem(name=name, qty=qty)
            db.session.add(it)
            db.session.commit()
            flash('Item added', 'success')
        return redirect(url_for('shopping_view'))
    items = ShoppingItem.query.order_by(ShoppingItem.id.desc()).all()
    return render_template('shopping.html', items=items)


@app.route('/shopping/<int:item_id>/toggle')
def toggle_item(item_id):
    it = ShoppingItem.query.get_or_404(item_id)
    it.bought = not it.bought
    db.session.commit()
    return redirect(request.referrer or url_for('shopping_view'))


@app.route('/members', methods=['GET', 'POST'])
def members_view():
    if request.method == 'POST':
        name = request.form.get('name')
        role = request.form.get('role')
        if not name:
            flash('Member name required', 'danger')
        else:
            m = Member(name=name, role=role)
            db.session.add(m)
            db.session.commit()
            flash('Member added', 'success')
        return redirect(url_for('members_view'))
    members = Member.query.all()
    return render_template('members.html', members=members)


if __name__ == '__main__':
    # Create DB tables inside the application context before serving.
    with app.app_context():
        create_tables()
    app.run(debug=True)
