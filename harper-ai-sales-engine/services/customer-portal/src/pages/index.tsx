import React, { useState } from 'react';
import Head from 'next/head';
import Link from 'next/link';

type ApplicationStatus = 'collecting_information' | 'reviewing' | 'submitted_to_carriers' | 'quotes_received' | 'bound';

interface Application {
  id: string;
  businessName: string;
  status: ApplicationStatus;
  submittedDate: string;
  lastUpdated: string;
  progress: number; // 0-100
  carriers: string[];
  nextSteps: string[];
  documents: { id: string; name: string; status: 'pending' | 'approved' | 'rejected' }[];
}

const mockApplications: Application[] = [
  {
    id: 'APP-2024001',
    businessName: 'Acme Retail Solutions',
    status: 'reviewing',
    submittedDate: '2024-04-15',
    lastUpdated: '2024-04-17',
    progress: 45,
    carriers: ['Insurance Co A', 'Insurance Co B'],
    nextSteps: ['Upload business license', 'Schedule risk assessment call'],
    documents: [
      { id: 'doc1', name: 'Business Application.pdf', status: 'approved' },
      { id: 'doc2', name: 'Financial Statements.pdf', status: 'pending' }
    ]
  },
  {
    id: 'APP-2024002',
    businessName: 'TechStart Solutions',
    status: 'submitted_to_carriers',
    submittedDate: '2024-04-10',
    lastUpdated: '2024-04-18',
    progress: 65,
    carriers: ['Insurance Co A', 'Insurance Co C', 'Insurance Co D'],
    nextSteps: ['Waiting for quotes from carriers'],
    documents: [
      { id: 'doc3', name: 'Business Application.pdf', status: 'approved' },
      { id: 'doc4', name: 'Financial Statements.pdf', status: 'approved' },
      { id: 'doc5', name: 'Risk Assessment Report.pdf', status: 'approved' }
    ]
  }
];

const statusLabels: Record<ApplicationStatus, string> = {
  collecting_information: 'Collecting Information',
  reviewing: 'Under Review',
  submitted_to_carriers: 'Submitted to Carriers',
  quotes_received: 'Quotes Received',
  bound: 'Policy Bound'
};

const Home = () => {
  const [applications] = useState<Application[]>(mockApplications);

  return (
    <div className="min-h-screen bg-gray-50">
      <Head>
        <title>Harper Insurance | Application Tracking</title>
        <meta name="description" content="Track your insurance application status" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <header className="bg-blue-800 text-white shadow-lg">
        <div className="container mx-auto px-4 py-6">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold">Harper Insurance</h1>
            <div className="flex items-center space-x-4">
              <Link href="/profile" className="hover:underline">Profile</Link>
              <Link href="/support" className="hover:underline">Support</Link>
              <button className="bg-white text-blue-800 px-4 py-2 rounded font-medium hover:bg-gray-100">
                Log Out
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-8">
          <h2 className="text-2xl font-semibold text-gray-800">Your Applications</h2>
          <button className="bg-blue-600 text-white px-4 py-2 rounded font-medium hover:bg-blue-700">
            Start New Application
          </button>
        </div>

        {applications.length === 0 ? (
          <div className="bg-white rounded-lg shadow-md p-8 text-center">
            <h3 className="text-xl font-medium text-gray-700 mb-4">No applications yet</h3>
            <p className="text-gray-600 mb-6">
              Start a new application to find the right insurance coverage for your business.
            </p>
            <button className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700">
              Start New Application
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-6">
            {applications.map((app) => (
              <div key={app.id} className="bg-white rounded-lg shadow-md overflow-hidden">
                <div className="px-6 py-4 border-b border-gray-200">
                  <div className="flex justify-between items-center">
                    <h3 className="text-xl font-semibold text-gray-800">{app.businessName}</h3>
                    <span className="px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                      {statusLabels[app.status]}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mt-1">Application ID: {app.id}</p>
                </div>

                <div className="px-6 py-4">
                  <div className="flex justify-between text-sm text-gray-600 mb-4">
                    <span>Submitted: {app.submittedDate}</span>
                    <span>Last Updated: {app.lastUpdated}</span>
                  </div>

                  <div className="mb-4">
                    <div className="flex justify-between mb-1">
                      <span className="text-sm font-medium text-gray-700">Progress</span>
                      <span className="text-sm font-medium text-gray-700">{app.progress}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2.5">
                      <div
                        className="bg-blue-600 h-2.5 rounded-full"
                        style={{ width: `${app.progress}%` }}
                      ></div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div>
                      <h4 className="font-medium text-gray-700 mb-2">Carriers</h4>
                      <ul className="text-sm text-gray-600">
                        {app.carriers.map((carrier, index) => (
                          <li key={index} className="mb-1">• {carrier}</li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-700 mb-2">Next Steps</h4>
                      <ul className="text-sm text-gray-600">
                        {app.nextSteps.map((step, index) => (
                          <li key={index} className="mb-1">• {step}</li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  <h4 className="font-medium text-gray-700 mb-2">Documents</h4>
                  <div className="bg-gray-50 rounded-md p-3">
                    {app.documents.map((doc) => (
                      <div key={doc.id} className="flex justify-between items-center py-2 border-b border-gray-100 last:border-b-0">
                        <span className="text-sm text-gray-700">{doc.name}</span>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          doc.status === 'approved' ? 'bg-green-100 text-green-800' :
                          doc.status === 'rejected' ? 'bg-red-100 text-red-800' :
                          'bg-yellow-100 text-yellow-800'
                        }`}>
                          {doc.status.charAt(0).toUpperCase() + doc.status.slice(1)}
                        </span>
                      </div>
                    ))}
                    <button className="mt-3 w-full py-2 bg-gray-200 text-gray-700 text-sm font-medium rounded hover:bg-gray-300">
                      Upload Document
                    </button>
                  </div>
                </div>

                <div className="px-6 py-3 bg-gray-50 border-t border-gray-200">
                  <div className="flex justify-end">
                    <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">
                      View Details
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      <footer className="bg-gray-800 text-white py-8">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <h3 className="text-lg font-semibold mb-4">Harper Insurance</h3>
              <p className="text-gray-400 text-sm">
                Providing AI-powered commercial insurance brokerage services to transform your business.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">Contact</h3>
              <p className="text-gray-400 text-sm">
                San Francisco, CA<br />
                help@harper-insurance.com<br />
                (415) 555-0123
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">Legal</h3>
              <ul className="text-gray-400 text-sm space-y-2">
                <li><Link href="/privacy" className="hover:text-white">Privacy Policy</Link></li>
                <li><Link href="/terms" className="hover:text-white">Terms of Service</Link></li>
              </ul>
            </div>
          </div>
          <div className="mt-8 pt-6 border-t border-gray-700 text-center text-gray-400 text-sm">
            &copy; {new Date().getFullYear()} Harper Insurance. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Home;
