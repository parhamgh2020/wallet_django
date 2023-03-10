from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from wallets.models import Wallet, Transaction
from utils import request_third_party_deposit


class WalletTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.wallet = Wallet.objects.create(owner=self.user)

    def test_initial_balance(self):
        self.assertEqual(self.wallet.balance, Decimal("0.00"))

    def test_deposit(self):
        deposit_amount = "100.50"
        message, success = self.wallet.deposit(deposit_amount)
        self.assertEqual(message, "deposited successfully")
        self.assertEqual(success, True)
        self.assertEqual(self.wallet.balance, Decimal(deposit_amount))

    def test_withdraw_insufficient_funds(self):
        withdraw_amount = "100.50"
        message, success = self.wallet.withdraw(withdraw_amount,
                                                request_third_party_deposit)
        self.assertEqual(message, "Insufficient funds.")
        self.assertEqual(success, False)
        self.assertEqual(self.wallet.balance, Decimal("0.00"))

    def test_withdraw_success(self):
        deposit_amount = "200.00"
        self.wallet.deposit(deposit_amount)
        withdraw_amount = "100.50"
        message, result = self.wallet.withdraw(withdraw_amount,
                                               request_third_party_deposit)
        if result:
            self.assertEqual(message, "success")
            self.assertEqual(self.wallet.balance, Decimal("99.50"))
        else:
            self.assertEqual(self.wallet.balance, Decimal("200.00"))


class TransactionTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser'
        )
        self.wallet = Wallet.objects.create(owner=self.user,
                                            balance=Decimal("500.00"))

    def test_deposit_transaction(self):
        deposit_amount = "100.50"
        transaction = Transaction.objects.create(wallet=self.wallet,
                                                 amount=Decimal(deposit_amount),
                                                 method=Transaction.Method.DEPOSIT)
        transaction.execute_deposit()
        self.assertEqual(transaction.status, Transaction.Status.COMPLETED)
        self.assertEqual(transaction.status_description, "deposited successfully")
        self.assertEqual(self.wallet.balance, Decimal("600.50"))


class WalletViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser')
        self.wallet = Wallet.objects.create(owner=self.user)

    def test_retrieve_wallet(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/wallets/wallets/{self.wallet.uuid}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(int(response.data['owner'][-2]), self.user.pk)

    def test_update_wallet(self):
        self.client.force_authenticate(user=self.user)
        data = {'balance': '1000.00'}
        response = self.client.patch(f'/wallets/wallets/{self.wallet.uuid}/', data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Wallet.objects.get(uuid=self.wallet.uuid).balance, 1000.00)

    def test_list_wallets(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/wallets/wallets/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)


class TransactionViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser')
        self.wallet = Wallet.objects.create(owner=self.user, balance=100)
        self.transaction = Transaction.objects.create(wallet=self.wallet,
                                                      amount=50.00)

    def test_create_transaction(self):
        self.client.force_authenticate(user=self.user)
        data = {'wallet': self.wallet.uuid,
                'amount': '50.00',
                'method': '0'}
        response = self.client.post('/wallets/transactions/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Transaction.objects.count(), 2)  # 1 created during setup, 1 created in this test
        self.assertEqual(Transaction.objects.last().wallet.pk, self.wallet.pk)

    def test_retrieve_transaction(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/wallets/transactions/{self.transaction.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['amount'], '50.00')

    def test_list_transactions(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/wallets/transactions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
