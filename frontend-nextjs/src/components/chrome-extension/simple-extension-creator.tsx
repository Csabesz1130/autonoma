'use client'

import { useState } from 'react'

interface ExtensionType {
  id: string
  name: string
  description: string
  complexity: string
  examples: string[]
}

interface Permission {
  id: string
  name: string
  description: string
  required_for: string[]
  risk_level: 'low' | 'medium' | 'high'
}

const extensionTypes: ExtensionType[] = [
  {
    id: 'popup',
    name: 'Popup Extension',
    description: 'Extension with a popup interface accessible from the browser toolbar',
    complexity: 'Simple',
    examples: ['Password generator', 'Unit converter', 'Quick notes']
  },
  {
    id: 'content_script',
    name: 'Content Script Extension',
    description: 'Extension that modifies or enhances web pages',
    complexity: 'Medium',
    examples: ['Ad blocker', 'Page translator', 'Social media enhancer']
  },
  {
    id: 'background',
    name: 'Background Extension',
    description: 'Extension with background processing capabilities',
    complexity: 'Advanced',
    examples: ['System monitor', 'Auto-backup', 'Notification manager']
  },
  {
    id: 'devtools',
    name: 'DevTools Extension',
    description: 'Extension that adds panels to Chrome Developer Tools',
    complexity: 'Advanced',
    examples: ['React DevTools', 'Performance profiler', 'API inspector']
  },
  {
    id: 'options',
    name: 'Options Extension',
    description: 'Extension with a dedicated options/settings page',
    complexity: 'Simple',
    examples: ['Theme customizer', 'Privacy settings', 'Feature toggles']
  }
]

const commonPermissions: Permission[] = [
  {
    id: 'storage',
    name: 'Storage',
    description: 'Store and retrieve data using Chrome\'s storage API',
    required_for: ['Settings', 'User data', 'Preferences'],
    risk_level: 'low'
  },
  {
    id: 'activeTab',
    name: 'Active Tab',
    description: 'Access the currently active tab',
    required_for: ['Current page modification', 'Tab information'],
    risk_level: 'medium'
  },
  {
    id: 'tabs',
    name: 'All Tabs',
    description: 'Access information about all tabs',
    required_for: ['Tab management', 'Multi-tab operations'],
    risk_level: 'high'
  },
  {
    id: 'notifications',
    name: 'Notifications',
    description: 'Display system notifications',
    required_for: ['User alerts', 'Status updates'],
    risk_level: 'low'
  },
  {
    id: 'webRequest',
    name: 'Web Requests',
    description: 'Monitor and modify network requests',
    required_for: ['Request blocking', 'Request modification'],
    risk_level: 'high'
  }
]

interface SimpleExtensionCreatorProps {
  onExtensionGenerated?: (extension: any) => void
}

export function SimpleExtensionCreator({ onExtensionGenerated }: SimpleExtensionCreatorProps) {
  const [step, setStep] = useState(1)
  const [prompt, setPrompt] = useState('')
  const [selectedType, setSelectedType] = useState<string>('')
  const [selectedPermissions, setSelectedPermissions] = useState<string[]>([])
  const [targetWebsites, setTargetWebsites] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [generationProgress, setGenerationProgress] = useState(0)
  const [analysis, setAnalysis] = useState<any>(null)
  const [generatedExtension, setGeneratedExtension] = useState<any>(null)
  const [debugLog, setDebugLog] = useState<string[]>([])

  const addDebugLog = (message: string, type: 'info' | 'error' | 'success' = 'info') => {
    const timestamp = new Date().toLocaleTimeString()
    const logEntry = `[${timestamp}] ${type.toUpperCase()}: ${message}`
    setDebugLog(prev => [...prev, logEntry])
    console.log(logEntry)
  }

  const handleAnalyzePrompt = async () => {
    if (!prompt.trim()) {
      addDebugLog('No prompt provided', 'error')
      return
    }

    try {
      setIsGenerating(true)
      setGenerationProgress(25)
      addDebugLog('Starting extension analysis...')

      // API call to analyze extension requirements
      const response = await fetch('/api/chrome-extension/analyze', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          // Add auth header if available
          ...(localStorage.getItem('auth_token') && {
            'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
          })
        },
        body: JSON.stringify({ prompt })
      })

      addDebugLog(`API Response Status: ${response.status}`)

      if (!response.ok) {
        const errorText = await response.text()
        addDebugLog(`API Error: ${response.status} ${response.statusText} - ${errorText}`, 'error')
        throw new Error(`Analysis failed: ${response.status} ${response.statusText}`)
      }

      const analysisData = await response.json()
      addDebugLog('Analysis completed successfully', 'success')
      setAnalysis(analysisData)
      setGenerationProgress(50)

      // Auto-suggest extension type and permissions based on analysis
      if (analysisData.recommendations?.suggested_type?.length > 0) {
        setSelectedType(analysisData.recommendations.suggested_type[0].type)
        addDebugLog(`Auto-selected extension type: ${analysisData.recommendations.suggested_type[0].type}`)
      }
      if (analysisData.recommendations?.required_permissions) {
        setSelectedPermissions(analysisData.recommendations.required_permissions)
        addDebugLog(`Auto-selected permissions: ${analysisData.recommendations.required_permissions.join(', ')}`)
      }

      setStep(2)
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Analysis failed. Please try again.'
      addDebugLog(`Analysis error: ${errorMessage}`, 'error')
      setAnalysis({
        error: errorMessage,
        recommendations: {
          complexity_score: 'Unknown',
          estimated_development_time: 'Unknown',
          required_permissions: []
        }
      })
    } finally {
      setIsGenerating(false)
      setGenerationProgress(0)
    }
  }

  const handleGenerateExtension = async () => {
    try {
      setIsGenerating(true)
      setGenerationProgress(0)
      addDebugLog('Starting extension generation...')

      // Simulate extension generation with progress updates
      const progressInterval = setInterval(() => {
        setGenerationProgress(prev => {
          if (prev >= 95) {
            clearInterval(progressInterval)
            return 95
          }
          return prev + 10
        })
      }, 500)

      // API call to generate extension
      const response = await fetch('/api/chrome-extension/generate', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          // Add auth header if available
          ...(localStorage.getItem('auth_token') && {
            'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
          })
        },
        body: JSON.stringify({
          prompt,
          extension_type: selectedType,
          permissions: selectedPermissions,
          target_websites: targetWebsites.split(',').map(s => s.trim()).filter(Boolean)
        })
      })

      addDebugLog(`Generation API Response Status: ${response.status}`)

      if (!response.ok) {
        const errorText = await response.text()
        addDebugLog(`Generation API Error: ${response.status} ${response.statusText} - ${errorText}`, 'error')
        throw new Error(`Extension generation failed: ${response.status} ${response.statusText}`)
      }

      const extensionData = await response.json()
      addDebugLog(`Extension generated successfully: ${extensionData.name}`, 'success')
      setGeneratedExtension(extensionData)
      setGenerationProgress(100)

      if (onExtensionGenerated) {
        onExtensionGenerated(extensionData)
      }

      setStep(3)
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Extension generation failed. Please try again.'
      addDebugLog(`Generation error: ${errorMessage}`, 'error')
      setGeneratedExtension({
        error: errorMessage,
        extension_id: '',
        name: '',
        description: '',
        extension_type: '',
        status: 'failed',
        install_instructions: []
      })
      setStep(3)
    } finally {
      setIsGenerating(false)
    }
  }

  const handleDownloadExtension = () => {
    if (generatedExtension?.download_url) {
      addDebugLog(`Downloading extension: ${generatedExtension.download_url}`)
      window.open(generatedExtension.download_url, '_blank')
    } else {
      addDebugLog('No download URL available', 'error')
    }
  }

  const getComplexityColor = (complexity: string) => {
    switch (complexity) {
      case 'Simple': return 'bg-green-100 text-green-800'
      case 'Medium': return 'bg-yellow-100 text-yellow-800'
      case 'Advanced': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'low': return 'bg-green-100 text-green-800'
      case 'medium': return 'bg-yellow-100 text-yellow-800'
      case 'high': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const togglePermission = (permissionId: string) => {
    setSelectedPermissions(prev => 
      prev.includes(permissionId)
        ? prev.filter(p => p !== permissionId)
        : [...prev, permissionId]
    )
    addDebugLog(`Permission toggled: ${permissionId}`)
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6 p-6">
      {/* Header */}
      <div className="text-center space-y-4">
        <div className="flex items-center justify-center space-x-3">
          <div className="h-10 w-10 text-blue-600">🔧</div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Chrome Extension Creator
          </h1>
        </div>
        <p className="text-gray-600 max-w-2xl mx-auto">
          Create powerful Chrome extensions with AI. From simple popup tools to advanced content scripts,
          generate complete browser extensions in minutes.
        </p>
      </div>

      {/* Progress Steps */}
      <div className="flex items-center justify-center space-x-4 py-4">
        {[1, 2, 3].map((stepNum) => (
          <div key={stepNum} className="flex items-center">
            <div className={`
              w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold
              ${step >= stepNum ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'}
            `}>
              {stepNum}
            </div>
            {stepNum < 3 && (
              <div className={`
                w-12 h-1 mx-2
                ${step > stepNum ? 'bg-blue-600' : 'bg-gray-200'}
              `} />
            )}
          </div>
        ))}
      </div>

      {/* Debug Panel */}
      <div className="bg-gray-50 border rounded-lg p-4">
        <div className="flex items-center justify-between mb-2">
          <h3 className="font-medium text-sm">Debug Log</h3>
          <button 
            onClick={() => setDebugLog([])}
            className="text-xs text-gray-500 hover:text-gray-700"
          >
            Clear
          </button>
        </div>
        <div className="bg-white border rounded p-2 h-24 overflow-y-auto">
          {debugLog.length === 0 ? (
            <p className="text-gray-400 text-sm">No debug messages yet...</p>
          ) : (
            debugLog.map((log, index) => (
              <div key={index} className="text-xs font-mono text-gray-700 mb-1">
                {log}
              </div>
            ))
          )}
        </div>
      </div>

      {/* Step 1: Describe Extension */}
      {step === 1 && (
        <div className="bg-white border rounded-lg shadow-sm">
          <div className="p-6">
            <div className="flex items-center space-x-2 mb-4">
              <span className="text-lg">✨</span>
              <h2 className="text-xl font-semibold">Describe Your Extension</h2>
            </div>
            <p className="text-gray-600 mb-6">
              Tell us what kind of Chrome extension you want to create
            </p>
            
            <div className="space-y-6">
              <div className="space-y-2">
                <label htmlFor="extension-prompt" className="block text-sm font-medium">
                  Extension Description
                </label>
                <textarea
                  id="extension-prompt"
                  placeholder="I want to create a Chrome extension that helps me track my daily productivity by monitoring the time I spend on different websites and showing me a summary at the end of the day..."
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  className="w-full min-h-[120px] p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {extensionTypes.slice(0, 4).map((type) => (
                  <div key={type.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer">
                    <div className="flex items-start space-x-3">
                      <div className="text-blue-600 mt-1">🔧</div>
                      <div>
                        <h3 className="font-semibold text-sm">{type.name}</h3>
                        <p className="text-xs text-gray-600 mt-1">{type.description}</p>
                        <span className={`inline-block mt-2 px-2 py-1 text-xs rounded ${getComplexityColor(type.complexity)}`}>
                          {type.complexity}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <button 
                onClick={handleAnalyzePrompt}
                disabled={!prompt.trim() || isGenerating}
                className="w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
              >
                {isGenerating ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
                    <span>Analyzing Your Idea...</span>
                  </>
                ) : (
                  <>
                    <span>⚡</span>
                    <span>Analyze Extension Idea</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Step 2: Configure Extension */}
      {step === 2 && (
        <div className="space-y-6">
          {/* Analysis Results */}
          {analysis && (
            <div className="bg-white border rounded-lg shadow-sm p-6">
              <h2 className="text-xl font-semibold mb-4">AI Analysis Results</h2>
              <p className="text-gray-600 mb-4">
                {analysis.error ? 'Analysis encountered an error' : 'Based on your description, here\'s what we recommend'}
              </p>
              
              {analysis.error ? (
                <div className="text-center p-4 bg-red-50 border border-red-200 rounded-lg">
                  <div className="text-red-600 font-medium">Analysis Failed</div>
                  <div className="text-sm text-red-500 mt-2">{analysis.error}</div>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">
                      {analysis.recommendations?.complexity_score || 'Medium'}
                    </div>
                    <div className="text-sm text-gray-600">Complexity</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">
                      {analysis.recommendations?.estimated_development_time || '15-30 min'}
                    </div>
                    <div className="text-sm text-gray-600">Est. Time</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-600">
                      {analysis.recommendations?.required_permissions?.length || 2}
                    </div>
                    <div className="text-sm text-gray-600">Permissions</div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Extension Configuration */}
          <div className="bg-white border rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-semibold mb-4">Configure Your Extension</h2>
            <p className="text-gray-600 mb-6">Select the extension type and required permissions</p>
            
            <div className="space-y-6">
              <div className="space-y-2">
                <label className="block text-sm font-medium">Extension Type</label>
                <select 
                  value={selectedType} 
                  onChange={(e) => setSelectedType(e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Select extension type</option>
                  {extensionTypes.map((type) => (
                    <option key={type.id} value={type.id}>
                      {type.name} ({type.complexity})
                    </option>
                  ))}
                </select>
              </div>

              <div className="space-y-3">
                <label className="block text-sm font-medium">Required Permissions</label>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {commonPermissions.map((permission) => (
                    <div key={permission.id} className="flex items-start space-x-3 p-3 border rounded-lg">
                      <input
                        type="checkbox"
                        id={permission.id}
                        checked={selectedPermissions.includes(permission.id)}
                        onChange={() => togglePermission(permission.id)}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded mt-1"
                      />
                      <div className="flex-1">
                        <label htmlFor={permission.id} className="text-sm font-medium cursor-pointer">
                          {permission.name}
                        </label>
                        <p className="text-xs text-gray-600 mt-1">
                          {permission.description}
                        </p>
                        <span className={`inline-block mt-1 px-2 py-1 text-xs rounded ${getRiskColor(permission.risk_level)}`}>
                          {permission.risk_level} risk
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {selectedType === 'content_script' && (
                <div className="space-y-2">
                  <label htmlFor="target-websites" className="block text-sm font-medium">
                    Target Websites (optional)
                  </label>
                  <input
                    type="text"
                    id="target-websites"
                    placeholder="example.com, *.google.com, https://github.com/*"
                    value={targetWebsites}
                    onChange={(e) => setTargetWebsites(e.target.value)}
                    className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                  <p className="text-xs text-gray-600">
                    Comma-separated list of websites where the extension should work
                  </p>
                </div>
              )}

              <div className="flex space-x-3">
                <button 
                  onClick={() => setStep(1)}
                  className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                >
                  Back
                </button>
                <button 
                  onClick={handleGenerateExtension}
                  disabled={!selectedType || isGenerating}
                  className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
                >
                  {isGenerating ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
                      <span>Generating Extension...</span>
                    </>
                  ) : (
                    <>
                      <span>🔧</span>
                      <span>Generate Extension</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Step 3: Download & Install */}
      {step === 3 && generatedExtension && (
        <div className="bg-white border rounded-lg shadow-sm p-6">
          <div className="flex items-center space-x-2 mb-4">
            <div className={`w-8 h-8 rounded-full ${generatedExtension.error ? 'bg-red-100' : 'bg-green-100'} flex items-center justify-center`}>
              <span>{generatedExtension.error ? '❌' : '✅'}</span>
            </div>
            <h2 className="text-xl font-semibold">
              {generatedExtension.error ? 'Extension Generation Failed' : 'Extension Generated Successfully!'}
            </h2>
          </div>
          <p className="text-gray-600 mb-6">
            {generatedExtension.error ? 
              'There was an error generating your extension' : 
              `Your Chrome extension "${generatedExtension.name}" is ready to download and install`
            }
          </p>
          
          {generatedExtension.error ? (
            <div className="text-center p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="text-red-600 font-medium">Generation Failed</div>
              <div className="text-sm text-red-500 mt-2">{generatedExtension.error}</div>
              <button 
                onClick={() => { setStep(1); setGeneratedExtension(null); setAnalysis(null); }} 
                className="mt-4 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700"
              >
                Try Again
              </button>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div>
                  <h3 className="font-semibold mb-3">Extension Details</h3>
                  <div className="space-y-2 text-sm">
                    <div><strong>Name:</strong> {generatedExtension.name}</div>
                    <div><strong>Type:</strong> {generatedExtension.extension_type}</div>
                    <div><strong>Status:</strong> 
                      <span className="ml-2 px-2 py-1 bg-green-100 text-green-800 rounded text-xs">
                        {generatedExtension.status}
                      </span>
                    </div>
                  </div>
                </div>
                
                <div>
                  <h3 className="font-semibold mb-3">Quick Actions</h3>
                  <div className="space-y-2">
                    <button 
                      onClick={handleDownloadExtension} 
                      className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 flex items-center justify-center space-x-2"
                    >
                      <span>⬇️</span>
                      <span>Download Extension</span>
                    </button>
                    <button className="w-full border border-gray-300 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-50 flex items-center justify-center space-x-2">
                      <span>📝</span>
                      <span>View Code</span>
                    </button>
                  </div>
                </div>
              </div>

              <div className="mb-6">
                <h3 className="font-semibold mb-3">Installation Instructions</h3>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <ol className="list-decimal list-inside space-y-2 text-sm">
                    {generatedExtension.install_instructions?.map((instruction: string, index: number) => (
                      <li key={index}>{instruction}</li>
                    ))}
                  </ol>
                </div>
              </div>

              <div className="flex space-x-3">
                <button 
                  onClick={() => { setStep(1); setGeneratedExtension(null); }}
                  className="border border-gray-300 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-50"
                >
                  Create Another Extension
                </button>
                <button 
                  onClick={handleDownloadExtension} 
                  className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 flex items-center justify-center space-x-2"
                >
                  <span>⬇️</span>
                  <span>Download & Install</span>
                </button>
              </div>
            </>
          )}
        </div>
      )}

      {/* Generation Progress */}
      {isGenerating && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-96">
            <div className="text-center space-y-4">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto" />
              <div>
                <h3 className="font-semibold">Generating Your Extension</h3>
                <p className="text-sm text-gray-600">
                  AI agents are working on your Chrome extension...
                </p>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300" 
                  style={{ width: `${generationProgress}%` }}
                />
              </div>
              <p className="text-xs text-gray-600">
                {generationProgress}% complete
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}