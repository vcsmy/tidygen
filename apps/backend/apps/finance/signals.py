"""
Signals for automated finance operations in TidyGen ERP platform.
"""
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.db import models
from datetime import timedelta
from decimal import Decimal

from apps.finance.models import (
    Invoice, InvoiceItem, Payment, Expense, Budget, BudgetItem,
    RecurringInvoice, RecurringInvoiceItem, Account
)


@receiver(post_save, sender=InvoiceItem)
def update_invoice_totals(sender, instance, created, **kwargs):
    """Update invoice totals when invoice items are saved."""
    invoice = instance.invoice
    
    # Calculate subtotal from all items
    subtotal = sum(item.total_price for item in invoice.items.all())
    invoice.subtotal = subtotal
    
    # Calculate tax amount
    tax_amount = (subtotal * invoice.tax_rate) / 100
    invoice.tax_amount = tax_amount
    
    # Calculate total amount
    invoice.total_amount = subtotal + tax_amount - invoice.discount_amount
    
    # Save without triggering signals again
    Invoice.objects.filter(pk=invoice.pk).update(
        subtotal=subtotal,
        tax_amount=tax_amount,
        total_amount=invoice.total_amount
    )


@receiver(post_delete, sender=InvoiceItem)
def update_invoice_totals_on_delete(sender, instance, **kwargs):
    """Update invoice totals when invoice items are deleted."""
    invoice = instance.invoice
    
    # Calculate subtotal from remaining items
    subtotal = sum(item.total_price for item in invoice.items.all())
    invoice.subtotal = subtotal
    
    # Calculate tax amount
    tax_amount = (subtotal * invoice.tax_rate) / 100
    invoice.tax_amount = tax_amount
    
    # Calculate total amount
    invoice.total_amount = subtotal + tax_amount - invoice.discount_amount
    
    # Save without triggering signals again
    Invoice.objects.filter(pk=invoice.pk).update(
        subtotal=subtotal,
        tax_amount=tax_amount,
        total_amount=invoice.total_amount
    )


@receiver(post_save, sender=Payment)
def update_invoice_paid_amount(sender, instance, created, **kwargs):
    """Update invoice paid amount when payment is saved."""
    if instance.invoice:
        invoice = instance.invoice
        
        # Calculate total paid amount from all payments
        total_paid = sum(payment.amount for payment in invoice.payments.all())
        invoice.paid_amount = total_paid
        
        # Update invoice status if fully paid
        if total_paid >= invoice.total_amount and invoice.status in ['sent', 'viewed']:
            invoice.status = 'paid'
            invoice.paid_date = timezone.now().date()
        
        # Save without triggering signals again
        Invoice.objects.filter(pk=invoice.pk).update(
            paid_amount=total_paid,
            status=invoice.status,
            paid_date=invoice.paid_date
        )


@receiver(post_delete, sender=Payment)
def update_invoice_paid_amount_on_delete(sender, instance, **kwargs):
    """Update invoice paid amount when payment is deleted."""
    if instance.invoice:
        invoice = instance.invoice
        
        # Calculate total paid amount from remaining payments
        total_paid = sum(payment.amount for payment in invoice.payments.all())
        invoice.paid_amount = total_paid
        
        # Update invoice status if not fully paid
        if total_paid < invoice.total_amount and invoice.status == 'paid':
            invoice.status = 'sent'  # or 'viewed' based on business logic
            invoice.paid_date = None
        
        # Save without triggering signals again
        Invoice.objects.filter(pk=invoice.pk).update(
            paid_amount=total_paid,
            status=invoice.status,
            paid_date=invoice.paid_date
        )


@receiver(post_save, sender=Expense)
def update_budget_spent_amount(sender, instance, created, **kwargs):
    """Update budget spent amount when expense is approved or paid."""
    if instance.status in ['approved', 'paid']:
        # Find matching budget items and update spent amounts
        budget_items = BudgetItem.objects.filter(
            budget__organization=instance.organization,
            budget__is_active=True,
            budget__start_date__lte=instance.expense_date,
            budget__end_date__gte=instance.expense_date,
            category=instance.category
        )
        
        for budget_item in budget_items:
            # Calculate total spent amount for this category in this budget period
            total_spent = Expense.objects.filter(
                organization=instance.organization,
                category=instance.category,
                expense_date__gte=budget_item.budget.start_date,
                expense_date__lte=budget_item.budget.end_date,
                status__in=['approved', 'paid']
            ).aggregate(total=models.Sum('total_amount'))['total'] or Decimal('0')
            
            budget_item.spent_amount = total_spent
            budget_item.save()
            
            # Update budget total spent amount
            budget = budget_item.budget
            budget_spent = BudgetItem.objects.filter(budget=budget).aggregate(
                total=models.Sum('spent_amount')
            )['total'] or Decimal('0')
            
            budget.spent_amount = budget_spent
            budget.save()


@receiver(post_delete, sender=Expense)
def update_budget_spent_amount_on_delete(sender, instance, **kwargs):
    """Update budget spent amount when expense is deleted."""
    if instance.status in ['approved', 'paid']:
        # Find matching budget items and update spent amounts
        budget_items = BudgetItem.objects.filter(
            budget__organization=instance.organization,
            budget__is_active=True,
            budget__start_date__lte=instance.expense_date,
            budget__end_date__gte=instance.expense_date,
            category=instance.category
        )
        
        for budget_item in budget_items:
            # Calculate total spent amount for this category in this budget period
            total_spent = Expense.objects.filter(
                organization=instance.organization,
                category=instance.category,
                expense_date__gte=budget_item.budget.start_date,
                expense_date__lte=budget_item.budget.end_date,
                status__in=['approved', 'paid']
            ).aggregate(total=models.Sum('total_amount'))['total'] or Decimal('0')
            
            budget_item.spent_amount = total_spent
            budget_item.save()
            
            # Update budget total spent amount
            budget = budget_item.budget
            budget_spent = BudgetItem.objects.filter(budget=budget).aggregate(
                total=models.Sum('spent_amount')
            )['total'] or Decimal('0')
            
            budget.spent_amount = budget_spent
            budget.save()


@receiver(post_save, sender=BudgetItem)
def update_budget_total_spent(sender, instance, created, **kwargs):
    """Update budget total spent amount when budget item is saved."""
    budget = instance.budget
    
    # Calculate total spent amount from all budget items
    total_spent = sum(item.spent_amount for item in budget.items.all())
    budget.spent_amount = total_spent
    
    # Save without triggering signals again
    Budget.objects.filter(pk=budget.pk).update(spent_amount=total_spent)


@receiver(post_delete, sender=BudgetItem)
def update_budget_total_spent_on_delete(sender, instance, **kwargs):
    """Update budget total spent amount when budget item is deleted."""
    budget = instance.budget
    
    # Calculate total spent amount from remaining budget items
    total_spent = sum(item.spent_amount for item in budget.items.all())
    budget.spent_amount = total_spent
    
    # Save without triggering signals again
    Budget.objects.filter(pk=budget.pk).update(spent_amount=total_spent)


@receiver(pre_save, sender=Invoice)
def set_invoice_due_date(sender, instance, **kwargs):
    """Set invoice due date if not provided."""
    if not instance.due_date and instance.customer:
        # Set due date based on customer payment terms
        payment_terms = instance.customer.payment_terms or 30
        instance.due_date = instance.issue_date + timedelta(days=payment_terms)


@receiver(pre_save, sender=Expense)
def calculate_expense_total(sender, instance, **kwargs):
    """Calculate expense total amount."""
    instance.total_amount = instance.amount + instance.tax_amount


@receiver(pre_save, sender=InvoiceItem)
def calculate_invoice_item_total(sender, instance, **kwargs):
    """Calculate invoice item total price."""
    instance.total_price = instance.quantity * instance.unit_price


@receiver(pre_save, sender=RecurringInvoiceItem)
def calculate_recurring_invoice_item_total(sender, instance, **kwargs):
    """Calculate recurring invoice item total price."""
    instance.total_price = instance.quantity * instance.unit_price


@receiver(pre_save, sender=RecurringInvoice)
def calculate_recurring_invoice_total(sender, instance, **kwargs):
    """Calculate recurring invoice total amount."""
    # Calculate subtotal from items
    subtotal = sum(item.total_price for item in instance.items.all())
    instance.subtotal = subtotal
    
    # Calculate tax amount
    tax_amount = (subtotal * instance.tax_rate) / 100
    instance.tax_amount = tax_amount
    
    # Calculate total amount
    instance.total_amount = subtotal + tax_amount


@receiver(pre_save, sender=RecurringInvoice)
def set_next_generation_date(sender, instance, **kwargs):
    """Set next generation date for recurring invoices."""
    if instance.is_active and not instance.next_generation:
        # Set next generation date based on frequency and interval
        if instance.frequency == 'daily':
            instance.next_generation = instance.start_date + timedelta(days=instance.interval)
        elif instance.frequency == 'weekly':
            instance.next_generation = instance.start_date + timedelta(weeks=instance.interval)
        elif instance.frequency == 'monthly':
            # Add months (approximate)
            instance.next_generation = instance.start_date + timedelta(days=30 * instance.interval)
        elif instance.frequency == 'quarterly':
            instance.next_generation = instance.start_date + timedelta(days=90 * instance.interval)
        elif instance.frequency == 'yearly':
            instance.next_generation = instance.start_date + timedelta(days=365 * instance.interval)


@receiver(post_save, sender=Account)
def update_account_balance(sender, instance, created, **kwargs):
    """Update account balance based on related transactions."""
    # This is a placeholder for more complex balance calculation logic
    # In a real implementation, you would calculate the balance based on
    # all related transactions (payments, expenses, etc.)
    pass


