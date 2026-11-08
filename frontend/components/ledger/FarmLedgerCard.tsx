"use client";

import React, { useState } from "react";
import type { FarmExpense, SaleTransaction } from "../../lib/api/types";

interface FarmLedgerCardProps {
  expenses: FarmExpense[];
  sales?: SaleTransaction[];
  onAddExpense?: (expense: {
    category: string;
    description: string;
    amount: number;
    transaction_date: string;
    payment_method: string;
    vendor_name?: string;
  }) => Promise<void>;
  onCorrectExpense?: (expenseId: string, newAmount: number, reason: string) => Promise<void>;
  labels: {
    title: string;
    subtitle: string;
    recordExpense: string;
    category: string;
    amount: string;
    description: string;
    transactionDate: string;
    paymentStatus: string;
    receiptAttached: string;
    correctAmount: string;
    correctionReason: string;
    categories: Record<string, string>;
  };
}

export const FarmLedgerCard: React.FC<FarmLedgerCardProps> = ({
  expenses,
  sales = [],
  onAddExpense,
  onCorrectExpense,
  labels,
}) => {
  const [showAddModal, setShowAddModal] = useState(false);
  const [category, setCategory] = useState("FERTILIZERS");
  const [description, setDescription] = useState("");
  const [amount, setAmount] = useState<number | "">("");
  const [txDate, setTxDate] = useState(new Date().toISOString().split("T")[0]);
  const [paymentMethod, setPaymentMethod] = useState("UPI");
  const [vendorName, setVendorName] = useState("");

  const [correctingExpenseId, setCorrectingExpenseId] = useState<string | null>(null);
  const [newAmount, setNewAmount] = useState<number | "">("");
  const [correctionReason, setCorrectionReason] = useState("");

  const totalExpenseNum = expenses.reduce((sum, e) => sum + parseFloat(e.amount || "0"), 0);
  const totalSalesNum = sales.reduce((sum, s) => sum + parseFloat(s.net_amount || "0"), 0);

  const handleSubmitExpense = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!amount || amount <= 0 || !description) return;
    if (onAddExpense) {
      await onAddExpense({
        category,
        description,
        amount: Number(amount),
        transaction_date: txDate,
        payment_method: paymentMethod,
        vendor_name: vendorName || undefined,
      });
      setShowAddModal(false);
      setDescription("");
      setAmount("");
    }
  };

  const handleCorrectSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!correctingExpenseId || !newAmount || newAmount <= 0 || !correctionReason) return;
    if (onCorrectExpense) {
      await onCorrectExpense(correctingExpenseId, Number(newAmount), correctionReason);
      setCorrectingExpenseId(null);
      setNewAmount("");
      setCorrectionReason("");
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-emerald-100 p-6 space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-800">{labels.title}</h2>
          <p className="text-sm text-slate-500">{labels.subtitle}</p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="inline-flex items-center px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-medium rounded-lg shadow-sm transition"
        >
          + {labels.recordExpense}
        </button>
      </div>

      {/* KPI Banners */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-lg">
          <span className="text-xs font-semibold uppercase text-rose-700 tracking-wider">Total Recorded Expenses</span>
          <p className="text-2xl font-black text-rose-900 mt-1">₹{totalExpenseNum.toLocaleString("en-IN", { minimumFractionDigits: 2 })}</p>
          <span className="text-xs text-rose-600">{expenses.length} transaction entries</span>
        </div>
        <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-lg">
          <span className="text-xs font-semibold uppercase text-emerald-700 tracking-wider">Total Realized Revenue</span>
          <p className="text-2xl font-black text-emerald-900 mt-1">₹{totalSalesNum.toLocaleString("en-IN", { minimumFractionDigits: 2 })}</p>
          <span className="text-xs text-emerald-600">{sales.length} verified sales</span>
        </div>
      </div>

      {/* Expense List */}
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm divide-y divide-slate-200">
          <thead>
            <tr className="text-xs text-slate-500 uppercase bg-slate-50">
              <th className="py-3 px-3">{labels.transactionDate}</th>
              <th className="py-3 px-3">{labels.category}</th>
              <th className="py-3 px-3">{labels.description}</th>
              <th className="py-3 px-3 text-right">{labels.amount}</th>
              <th className="py-3 px-3 text-center">{labels.paymentStatus}</th>
              <th className="py-3 px-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {expenses.length === 0 ? (
              <tr>
                <td colSpan={6} className="py-6 text-center text-slate-400">
                  No recorded expenses yet. Click above to record seasonal inputs.
                </td>
              </tr>
            ) : (
              expenses.map((exp) => (
                <tr key={exp.id} className="hover:bg-slate-50 transition">
                  <td className="py-3 px-3 font-mono text-xs text-slate-600">{exp.transaction_date}</td>
                  <td className="py-3 px-3">
                    <span className="inline-block px-2 py-0.5 text-xs font-medium rounded-full bg-slate-100 text-slate-700">
                      {labels.categories[exp.category] || exp.category}
                    </span>
                  </td>
                  <td className="py-3 px-3 text-slate-800">
                    <div>{exp.description}</div>
                    {exp.vendor_name && <span className="text-xs text-slate-400">Vendor: {exp.vendor_name}</span>}
                    {exp.corrections && exp.corrections.length > 0 && (
                      <span className="ml-2 inline-block text-[10px] bg-amber-100 text-amber-800 px-1.5 py-0.2 rounded font-semibold">
                        Corrected ({exp.corrections.length})
                      </span>
                    )}
                  </td>
                  <td className="py-3 px-3 text-right font-mono font-bold text-slate-900">
                    ₹{parseFloat(exp.amount).toFixed(2)}
                  </td>
                  <td className="py-3 px-3 text-center">
                    <span className={`px-2 py-0.5 text-xs rounded-full font-medium ${
                      exp.payment_status === "PAID" ? "bg-emerald-100 text-emerald-800" : "bg-amber-100 text-amber-800"
                    }`}>
                      {exp.payment_status}
                    </span>
                  </td>
                  <td className="py-3 px-3 text-right">
                    <button
                      onClick={() => {
                        setCorrectingExpenseId(exp.id);
                        setNewAmount(parseFloat(exp.amount));
                      }}
                      className="text-xs text-emerald-600 hover:text-emerald-800 underline font-medium"
                    >
                      {labels.correctAmount}
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Record Expense Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl max-w-md w-full p-6 space-y-4 shadow-xl">
            <h3 className="text-lg font-bold text-slate-800">{labels.recordExpense}</h3>
            <form onSubmit={handleSubmitExpense} className="space-y-3">
              <div>
                <label className="block text-xs font-medium text-slate-700">{labels.category}</label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="mt-1 w-full border border-slate-300 rounded-lg p-2 text-sm focus:ring-emerald-500 focus:border-emerald-500"
                >
                  {Object.entries(labels.categories).map(([k, v]) => (
                    <option key={k} value={k}>{v}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-700">{labels.description}</label>
                <input
                  type="text"
                  required
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="e.g. 5 bags Urea 45kg from Warangal PACS"
                  className="mt-1 w-full border border-slate-300 rounded-lg p-2 text-sm"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-700">{labels.amount}</label>
                  <input
                    type="number"
                    step="0.01"
                    min="1"
                    required
                    value={amount}
                    onChange={(e) => setAmount(Number(e.target.value))}
                    className="mt-1 w-full border border-slate-300 rounded-lg p-2 text-sm font-mono"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-700">{labels.transactionDate}</label>
                  <input
                    type="date"
                    required
                    value={txDate}
                    onChange={(e) => setTxDate(e.target.value)}
                    className="mt-1 w-full border border-slate-300 rounded-lg p-2 text-sm"
                  />
                </div>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-700">Vendor / PACS Name</label>
                <input
                  type="text"
                  value={vendorName}
                  onChange={(e) => setVendorName(e.target.value)}
                  placeholder="e.g. PACS Warangal / Local Agro Agency"
                  className="mt-1 w-full border border-slate-300 rounded-lg p-2 text-sm"
                />
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 border border-slate-300 rounded-lg text-sm text-slate-600 hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-sm font-medium"
                >
                  Save Entry
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Financial Correction Modal */}
      {correctingExpenseId && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl max-w-md w-full p-6 space-y-4 shadow-xl">
            <h3 className="text-lg font-bold text-slate-800">{labels.correctAmount}</h3>
            <p className="text-xs text-slate-500">
              In accordance with ACREVIA audit governance, expense modifications are logged with an immutable audit trail.
            </p>
            <form onSubmit={handleCorrectSubmit} className="space-y-3">
              <div>
                <label className="block text-xs font-medium text-slate-700">Corrected Amount (₹)</label>
                <input
                  type="number"
                  step="0.01"
                  min="1"
                  required
                  value={newAmount}
                  onChange={(e) => setNewAmount(Number(e.target.value))}
                  className="mt-1 w-full border border-slate-300 rounded-lg p-2 text-sm font-mono"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-700">{labels.correctionReason}</label>
                <textarea
                  required
                  rows={3}
                  value={correctionReason}
                  onChange={(e) => setCorrectionReason(e.target.value)}
                  placeholder="e.g. Discount/rebate voucher applied by cooperative society upon invoice settlement."
                  className="mt-1 w-full border border-slate-300 rounded-lg p-2 text-sm"
                />
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setCorrectingExpenseId(null)}
                  className="px-4 py-2 border border-slate-300 rounded-lg text-sm text-slate-600 hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg text-sm font-medium"
                >
                  Save Correction
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
