import React from 'react'
import { DollarSign, CreditCard, PiggyBank, TrendingUp, Building, Shield } from 'lucide-react'
import { Card } from '../components/ui/Card'
import { Button } from '../components/ui/Button'

interface FinancialAccount {
  id: string
  institution: string
  type: string
  accountNumber: string
  value?: string
  notes?: string
  beneficiaries?: string[]
}

const FinancialMap: React.FC = () => {
  const [accounts, setAccounts] = React.useState<FinancialAccount[]>([])

  const accountTypes = [
    { id: 'bank', label: 'Bank Accounts', icon: <Building className="w-5 h-5" /> },
    { id: 'investment', label: 'Investments', icon: <TrendingUp className="w-5 h-5" /> },
    { id: 'retirement', label: 'Retirement', icon: <PiggyBank className="w-5 h-5" /> },
    { id: 'credit', label: 'Credit Cards', icon: <CreditCard className="w-5 h-5" /> },
    { id: 'insurance', label: 'Insurance', icon: <Shield className="w-5 h-5" /> },
    { id: 'crypto', label: 'Crypto', icon: <DollarSign className="w-5 h-5" /> }
  ]

  const totalValue = accounts.reduce((sum, acc) => {
    const value = acc.value?.replace(/[^0-9.-]+/g, '')
    return sum + (parseFloat(value || '0') || 0)
  }, 0)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-semibold text-warmGray-900 dark:text-warmGray-100 mb-2">
          Financial Map
        </h2>
        <p className="text-warmGray-600 dark:text-warmGray-400">
          Document your financial assets and accounts for your family
        </p>
      </div>

      {/* Total Value Card */}
      <Card className="bg-gradient-to-r from-emerald-500 to-teal-500 text-white">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm opacity-80">Estimated Total</p>
            <p className="text-4xl font-bold">
              ${totalValue.toLocaleString()}
            </p>
          </div>
          <div className="w-16 h-16 rounded-full bg-white/20 flex items-center justify-center">
            <DollarSign className="w-8 h-8" />
          </div>
        </div>
      </Card>

      {/* Account Types */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {accountTypes.map(type => {
          const count = accounts.filter(a => a.type === type.id).length
          return (
            <Card key={type.id} hover className="cursor-pointer">
              <div className="flex items-center gap-3 mb-2">
                <div className="w-10 h-10 rounded-lg bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center text-emerald-600 dark:text-emerald-400">
                  {type.icon}
                </div>
                <div>
                  <p className="font-medium text-warmGray-900 dark:text-warmGray-100">
                    {type.label}
                  </p>
                  <p className="text-sm text-warmGray-500">
                    {count} account{count !== 1 ? 's' : ''}
                  </p>
                </div>
              </div>
            </Card>
          )
        })}
      </div>

      {/* Accounts List */}
      <div className="space-y-3">
        <div className="flex justify-between items-center">
          <h3 className="text-lg font-medium text-warmGray-900 dark:text-warmGray-100">
            Your Accounts
          </h3>
          <Button size="sm">
            Add Account
          </Button>
        </div>

        {accounts.length === 0 ? (
          <Card className="text-center py-12">
            <DollarSign className="w-12 h-12 mx-auto text-warmGray-300 mb-4" />
            <h3 className="text-lg font-medium text-warmGray-900 dark:text-warmGray-100 mb-2">
              No accounts added yet
            </h3>
            <p className="text-warmGray-500 mb-4">
              Start documenting your financial assets
            </p>
          </Card>
        ) : (
          accounts.map(account => (
            <Card key={account.id}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-xl bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center text-emerald-600 dark:text-emerald-400">
                    <Building className="w-6 h-6" />
                  </div>
                  <div>
                    <h4 className="font-medium text-warmGray-900 dark:text-warmGray-100">
                      {account.institution}
                    </h4>
                    <p className="text-sm text-warmGray-500">
                      {account.type} • {account.accountNumber}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-medium text-warmGray-900 dark:text-warmGray-100">
                    {account.value || 'Value unknown'}
                  </p>
                </div>
              </div>
            </Card>
          ))
        )}
      </div>

      {/* Documents Section */}
      <Card>
        <h3 className="font-medium text-warmGray-900 dark:text-warmGray-100 mb-4">
          Important Documents
        </h3>
        <p className="text-warmGray-500 text-sm mb-4">
          Store references to important financial documents (not the documents themselves)
        </p>
        <div className="grid grid-cols-2 gap-4">
          <div className="p-4 border border-dashed border-warmGray-200 dark:border-warmGray-600 rounded-lg text-center cursor-pointer hover:bg-warmGray-50 dark:hover:bg-warmGray-700/50">
            <p className="text-sm text-warmGray-500">Will</p>
          </div>
          <div className="p-4 border border-dashed border-warmGray-200 dark:border-warmGray-600 rounded-lg text-center cursor-pointer hover:bg-warmGray-50 dark:hover:bg-warmGray-700/50">
            <p className="text-sm text-warmGray-500">Trust Documents</p>
          </div>
          <div className="p-4 border border-dashed border-warmGray-200 dark:border-warmGray-600 rounded-lg text-center cursor-pointer hover:bg-warmGray-50 dark:hover:bg-warmGray-700/50">
            <p className="text-sm text-warmGray-500">Insurance Policies</p>
          </div>
          <div className="p-4 border border-dashed border-warmGray-200 dark:border-warmGray-600 rounded-lg text-center cursor-pointer hover:bg-warmGray-50 dark:hover:bg-warmGray-700/50">
            <p className="text-sm text-warmGray-500">Tax Returns</p>
          </div>
        </div>
      </Card>
    </div>
  )
}

export default FinancialMap
