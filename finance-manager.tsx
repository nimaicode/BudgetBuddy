import { useState, useEffect } from 'react'
import { Plus, Minus, Search, ArrowRight, Trash } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts'

interface Transaction {
  id: number
  type: 'income' | 'expense'
  amount:                       
  category: string
  date: string
  description: string
}

interface Stock {
  symbol: string
  quantity: number
  price: number
  history: { date: string; price: number }[]
}

export default function FinanceManager() {
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [newTransaction, setNewTransaction] = useState<Transaction>({
    id: Date.now(),
    type: 'income',
    amount: 0,
    category: '',
    date: new Date().toISOString().split('T')[0],
    description: '',
  })
  const [searchTerm, setSearchTerm] = useState('')
  const [filterCategory, setFilterCategory] = useState('')
  const [filterMinAmount, setFilterMinAmount] = useState('')
  const [filterMaxAmount, setFilterMaxAmount] = useState('')
  const [creditCardBalance, setCreditCardBalance] = useState(0)
  const [stocks, setStocks] = useState<Stock[]>([
    { symbol: 'AAPL', quantity: 10, price: 150, history: [] },
    { symbol: 'GOOGL', quantity: 5, price: 2800, history: [] },
  ])

  useEffect(() => {
    // Simulate fetching stock prices
    const fetchStockPrices = async () => {
      const newStocks = stocks.map((stock) => ({
        ...stock,
        price: stock.price + Math.random() * 10 - 5, // Simulate price change
        history: [
          ...stock.history,
          { date: new Date().toISOString().split('T')[0], price: stock.price },
        ],
      }))
      setStocks(newStocks)
    }

    fetchStockPrices()
    const interval = setInterval(fetchStockPrices, 5000) // Update every 5 seconds

    return () => clearInterval(interval)
  }, [stocks])

  const addTransaction = () => {
    setTransactions([...transactions, newTransaction])
    setNewTransaction({
      id: Date.now(),
      type: 'income',
      amount: 0,
      category: '',
      date: new Date().toISOString().split('T')[0],
      description: '',
    })
  }

  const updateTransaction = (id: number, updatedTransaction: Transaction) => {
    setTransactions(
      transactions.map((transaction) =>
        transaction.id === id ? updatedTransaction : transaction
      )
    )
  }

  const deleteTransaction = (id: number) => {
    setTransactions(transactions.filter((transaction) => transaction.id !== id))
  }

  const calculateBalance = () => {
    return transactions.reduce((balance, transaction) => {
      return balance + (transaction.type === 'income' ? transaction.amount : -transaction.amount)
    }, 0)
  }

  const filteredTransactions = transactions
    .filter((transaction) =>
      transaction.description.toLowerCase().includes(searchTerm.toLowerCase())
    )
    .filter((transaction) =>
      filterCategory ? transaction.category === filterCategory : true
    )
    .filter((transaction) =>
      filterMinAmount ? transaction.amount >= parseFloat(filterMinAmount) : true
    )
    .filter((transaction) =>
      filterMaxAmount ? transaction.amount <= parseFloat(filterMaxAmount) : true
    )

  const expenseCategories = Array.from(
    new Set(transactions.filter((t) => t.type === 'expense').map((t) => t.category))
  )

  const categorySummaries = expenseCategories.map((category) => ({
    category,
    total: transactions
      .filter((t) => t.type === 'expense' && t.category === category)
      .reduce((sum, t) => sum + t.amount, 0),
  }))

  const totalStockValue = stocks.reduce((total, stock) => total + stock.quantity * stock.price, 0)

  return (
    <div className="bg-white min-h-screen flex flex-col">
      <header className="bg-blue-500 text-white shadow-lg">
        <div className="container mx-auto px-4 py-6 flex justify-between items-center">
          <h1 className="text-2xl font-bold">Finance Manager</h1>
        </div>
      </header>

      <main className="flex-grow container mx-auto px-4 py-8">
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-4">Add Transaction</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Type</label>
              <select
                className="mt-1 block w-full p-2 border border-gray-300 rounded-md"
                value={newTransaction.type}
                onChange={(e) =>
                  setNewTransaction({ ...newTransaction, type: e.target.value as 'income' | 'expense' })
                }
              >
                <option value="income">Income</option>
                <option value="expense">Expense</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Amount</label>
              <input
                type="number"
                className="mt-1 block w-full p-2 border border-gray-300 rounded-md"
                value={newTransaction.amount}
                onChange={(e) =>
                  setNewTransaction({ ...newTransaction, amount: parseFloat(e.target.value) })
                }
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Category</label>
              <input
                type="text"
                className="mt-1 block w-full p-2 border border-gray-300 rounded-md"
                value={newTransaction.category}
                onChange={(e) =>
                  setNewTransaction({ ...newTransaction, category: e.target.value })
                }
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Date</label>
              <input
                type="date"
                className="mt-1 block w-full p-2 border border-gray-300 rounded-md"
                value={newTransaction.date}
                onChange={(e) =>
                  setNewTransaction({ ...newTransaction, date: e.target.value })
                }
              />
            </div>
            <div className="col-span-2">
              <label className="block text-sm font-medium text-gray-700">Description</label>
              <input
                type="text"
                className="mt-1 block w-full p-2 border border-gray-300 rounded-md"
                value={newTransaction.description}
                onChange={(e) =>
                  setNewTransaction({ ...newTransaction, description: e.target.value })
                }
              />
            </div>
            <div className="col-span-2 flex justify-end">
              <button
                className="bg-blue-500 text-white px-4 py-2 rounded-md"
                onClick={addTransaction}
              >
                Add Transaction
              </button>
            </div>
          </div>
        </div>

        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-4">Transactions</h2>
          <div className="mb-4 flex space-x-4">
            <input
              type="text"
              placeholder="Search by description"
              className="p-2 border border-gray-300 rounded-md"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <select
              className="p-2 border border-gray-300 rounded-md"
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
            >
              <option value="">All Categories</option>
              {expenseCategories.map((category) => (
                <option key={category} value={category}>
                  {category}
                </option>
              ))}
            </select>
            <input
              type="number"
              placeholder="Min Amount"
              className="p-2 border border-gray-300 rounded-md"
              value={filterMinAmount}
              onChange={(e) => setFilterMinAmount(e.target.value)}
            />
            <input
              type="number"
              placeholder="Max Amount"
              className="p-2 border border-gray-300 rounded-md"
              value={filterMaxAmount}
              onChange={(e) => setFilterMaxAmount(e.target.value)}
            />
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Amount
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Category
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Description
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredTransactions.map((transaction) => (
                  <tr key={transaction.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {transaction.type}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {transaction.amount.toFixed(2)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {transaction.category}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {transaction.date}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {transaction.description}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        className="text-indigo-600 hover:text-indigo-900 mr-2"
                        onClick={() =>
                          updateTransaction(transaction.id, {
                            ...transaction,
                            amount: transaction.amount + 10, // Example update
                          })
                        }
                      >
                        <Plus className="h-4 w-4" />
                      </button>
                      <button
                        className="text-red-600 hover:text-red-900 mr-2"
                        onClick={() =>
                          updateTransaction(transaction.id, {
                            ...transaction,
                            amount: transaction.amount - 10, // Example update
                          })
                        }
                      >
                        <Minus className="h-4 w-4" />
                      </button>
                      <button
                        className="text-gray-600 hover:text-gray-900"
                        onClick={() => deleteTransaction(transaction.id)}
                      >
                        <Trash className="h-4 w-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-4">Balance</h2>
          <div className="bg-gray-100 p-4 rounded-md">
            <p className="text-2xl font-bold">
              Current Balance: ${calculateBalance().toFixed(2)}
            </p>
          </div>
        </div>

        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-4">Expense Summaries</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {categorySummaries.map((summary) => (
              <div key={summary.category} className="bg-gray-100 p-4 rounded-md">
                <p className="text-lg font-bold">{summary.category}</p>
                <p className="text-gray-500">Total: ${summary.total.toFixed(2)}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-4">Credit Card Balance</h2>
          <div className="bg-gray-100 p-4 rounded-md">
            <p className="text-2xl font-bold">
              Credit Card Balance: ${creditCardBalance.toFixed(2)}
            </p>
            <div className="mt-4 flex space-x-4">
              <button
                className="bg-green-500 text-white px-4 py-2 rounded-md"
                onClick={() => setCreditCardBalance(creditCardBalance + 100)} // Example update
              >
                Add $100
              </button>
              <button
                className="bg-red-500 text-white px-4 py-2 rounded-md"
                onClick={() => setCreditCardBalance(creditCardBalance - 100)} // Example update
              >
                Subtract $100
              </button>
            </div>
          </div>
        </div>

        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-4">Stocks</h2>
          <div className="bg-gray-100 p-4 rounded-md">
            <p className="text-2xl font-bold">
              Total Stock Value: ${totalStockValue.toFixed(2)}
            </p>
            <div className="mt-4">
              {stocks.map((stock) => (
                <div key={stock.symbol} className="mb-4">
                  <h3 className="text-lg font-bold">{stock.symbol}</h3>
                  <p className="text-gray-500">Quantity: {stock.quantity}</p>
                  <p className="text-gray-500">Current Price: ${stock.price.toFixed(2)}</p>
                  <p className="text-gray-500">Value: ${(stock.quantity * stock.price).toFixed(2)}</p>
                  <div className="mt-4">
                    <LineChart
                      width={500}
                      height={300}
                      data={stock.history}
                      margin={{
                        top: 5,
                        right: 30,
                        left: 20,
                        bottom: 5,
                      }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Line type="monotone" dataKey="price" stroke="#8884d8" activeDot={{ r: 8 }} />
                    </LineChart>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

