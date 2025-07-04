'use client'

import React, { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Checkbox } from '@/components/ui/checkbox'
import { Label } from '@/components/ui/label'
import { Progress } from '@/components/ui/progress'
import { 
  Extension, 
  Download, 
  Play, 
  Settings, 
  Code, 
  Chrome,
  Puzzle,
  Monitor,
  Shield,
  Clock,
  Zap,
  Sparkles
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

interface ExtensionType {
  id: string
  name: string
  description: string
  complexity: string
  examples: string[]
  icon: React.ComponentType<any>
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
    examples: ['Password generator', 'Unit converter', 'Quick notes'],
    icon: Extension
  },
  {
    id: 'content_script',
    name: 'Content Script Extension',
    description: 'Extension that modifies or enhances web pages',
    complexity: 'Medium',
    examples: ['Ad blocker', 'Page translator', 'Social media enhancer'],
    icon: Code
  },
  {
    id: 'background',
    name: 'Background Extension',
    description: 'Extension with background processing capabilities',
    complexity: 'Advanced',
    examples: ['System monitor', 'Auto-backup', 'Notification manager'],
    icon: Monitor
  },
  {
    id: 'devtools',
    name: 'DevTools Extension',
    description: 'Extension that adds panels to Chrome Developer Tools',
    complexity: 'Advanced',
    examples: ['React DevTools', 'Performance profiler', 'API inspector'],
    icon: Settings
  },
  {
    id: 'options',
    name: 'Options Extension',
    description: 'Extension with a dedicated options/settings page',
    complexity: 'Simple',
    examples: ['Theme customizer', 'Privacy settings', 'Feature toggles'],
    icon: Settings
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

interface ChromeExtensionCreatorProps {
  onExtensionGenerated?: (extension: any) => void
}

export function ChromeExtensionCreator({ onExtensionGenerated }: ChromeExtensionCreatorProps) {
  const [step, setStep] = useState(1)
  const [prompt, setPrompt] = useState('')
  const [selectedType, setSelectedType] = useState<string>('')
  const [selectedPermissions, setSelectedPermissions] = useState<string[]>([])
  const [targetWebsites, setTargetWebsites] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [generationProgress, setGenerationProgress] = useState(0)
  const [analysis, setAnalysis] = useState<any>(null)
  const [generatedExtension, setGeneratedExtension] = useState<any>(null)

  const handleAnalyzePrompt = async () => {
    if (!prompt.trim()) return

    try {
      setIsGenerating(true)
      setGenerationProgress(25)

      // Simulate API call to analyze extension requirements
      const response = await fetch('/api/chrome-extension/analyze', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        // In real implementation: body: JSON.stringify({ prompt })
      })

      const analysisData = await response.json()
      setAnalysis(analysisData)
      setGenerationProgress(50)

      // Auto-suggest extension type and permissions based on analysis
      if (analysisData.recommendations?.suggested_type?.length > 0) {
        setSelectedType(analysisData.recommendations.suggested_type[0].type)
      }
      if (analysisData.recommendations?.required_permissions) {
        setSelectedPermissions(analysisData.recommendations.required_permissions)
      }

      setStep(2)
    } catch (error) {
      console.error('Analysis failed:', error)
    } finally {
      setIsGenerating(false)
      setGenerationProgress(0)
    }
  }

  const handleGenerateExtension = async () => {
    try {
      setIsGenerating(true)
      setGenerationProgress(0)

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

      // Simulate API call to generate extension
      const response = await fetch('/api/chrome-extension/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt,
          extension_type: selectedType,
          permissions: selectedPermissions,
          target_websites: targetWebsites.split(',').map(s => s.trim()).filter(Boolean)
        })
      })

      const extensionData = await response.json()
      setGeneratedExtension(extensionData)
      setGenerationProgress(100)

      if (onExtensionGenerated) {
        onExtensionGenerated(extensionData)
      }

      setStep(3)
    } catch (error) {
      console.error('Extension generation failed:', error)
    } finally {
      setIsGenerating(false)
    }
  }

  const handleDownloadExtension = () => {
    if (generatedExtension?.download_url) {
      window.open(generatedExtension.download_url, '_blank')
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

  return (
    <div className="max-w-4xl mx-auto space-y-6 p-6">
      {/* Header */}
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center space-y-4"
      >
        <div className="flex items-center justify-center space-x-3">
          <Chrome className="h-10 w-10 text-blue-600" />
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Chrome Extension Creator
          </h1>
        </div>
        <p className="text-muted-foreground max-w-2xl mx-auto">
          Create powerful Chrome extensions with AI. From simple popup tools to advanced content scripts,
          generate complete browser extensions in minutes.
        </p>
      </motion.div>

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

      <AnimatePresence mode="wait">
        {/* Step 1: Describe Extension */}
        {step === 1 && (
          <motion.div
            key="step1"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
          >
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Sparkles className="h-5 w-5" />
                  <span>Describe Your Extension</span>
                </CardTitle>
                <CardDescription>
                  Tell us what kind of Chrome extension you want to create
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-2">
                  <Label htmlFor="extension-prompt">Extension Description</Label>
                  <Textarea
                    id="extension-prompt"
                    placeholder="I want to create a Chrome extension that helps me track my daily productivity by monitoring the time I spend on different websites and showing me a summary at the end of the day..."
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    className="min-h-[120px]"
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {extensionTypes.slice(0, 4).map((type) => (
                    <Card key={type.id} className="cursor-pointer hover:shadow-md transition-shadow">
                      <CardContent className="p-4">
                        <div className="flex items-start space-x-3">
                          <type.icon className="h-6 w-6 text-blue-600 mt-1" />
                          <div>
                            <h3 className="font-semibold text-sm">{type.name}</h3>
                            <p className="text-xs text-muted-foreground mt-1">{type.description}</p>
                            <Badge className={`mt-2 text-xs ${getComplexityColor(type.complexity)}`}>
                              {type.complexity}
                            </Badge>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>

                <Button 
                  onClick={handleAnalyzePrompt}
                  disabled={!prompt.trim() || isGenerating}
                  className="w-full"
                  size="lg"
                >
                  {isGenerating ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                      Analyzing Your Idea...
                    </>
                  ) : (
                    <>
                      <Zap className="mr-2 h-4 w-4" />
                      Analyze Extension Idea
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Step 2: Configure Extension */}
        {step === 2 && (
          <motion.div
            key="step2"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
          >
            {/* Analysis Results */}
            {analysis && (
              <Card>
                <CardHeader>
                  <CardTitle>AI Analysis Results</CardTitle>
                  <CardDescription>Based on your description, here's what we recommend</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-600">
                        {analysis.recommendations?.complexity_score || 'Medium'}
                      </div>
                      <div className="text-sm text-muted-foreground">Complexity</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">
                        {analysis.recommendations?.estimated_development_time || '15-30 min'}
                      </div>
                      <div className="text-sm text-muted-foreground">Est. Time</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-purple-600">
                        {analysis.recommendations?.required_permissions?.length || 2}
                      </div>
                      <div className="text-sm text-muted-foreground">Permissions</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Extension Configuration */}
            <Card>
              <CardHeader>
                <CardTitle>Configure Your Extension</CardTitle>
                <CardDescription>Select the extension type and required permissions</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-2">
                  <Label>Extension Type</Label>
                  <Select value={selectedType} onValueChange={setSelectedType}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select extension type" />
                    </SelectTrigger>
                    <SelectContent>
                      {extensionTypes.map((type) => (
                        <SelectItem key={type.id} value={type.id}>
                          <div className="flex items-center space-x-2">
                            <span>{type.name}</span>
                            <Badge className={getComplexityColor(type.complexity)}>
                              {type.complexity}
                            </Badge>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-3">
                  <Label>Required Permissions</Label>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {commonPermissions.map((permission) => (
                      <div key={permission.id} className="flex items-start space-x-3 p-3 border rounded-lg">
                        <Checkbox
                          id={permission.id}
                          checked={selectedPermissions.includes(permission.id)}
                          onCheckedChange={(checked) => {
                            if (checked) {
                              setSelectedPermissions([...selectedPermissions, permission.id])
                            } else {
                              setSelectedPermissions(selectedPermissions.filter(p => p !== permission.id))
                            }
                          }}
                        />
                        <div className="flex-1">
                          <Label htmlFor={permission.id} className="text-sm font-medium">
                            {permission.name}
                          </Label>
                          <p className="text-xs text-muted-foreground mt-1">
                            {permission.description}
                          </p>
                          <Badge className={`mt-1 text-xs ${getRiskColor(permission.risk_level)}`}>
                            {permission.risk_level} risk
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {selectedType === 'content_script' && (
                  <div className="space-y-2">
                    <Label htmlFor="target-websites">Target Websites (optional)</Label>
                    <Input
                      id="target-websites"
                      placeholder="example.com, *.google.com, https://github.com/*"
                      value={targetWebsites}
                      onChange={(e) => setTargetWebsites(e.target.value)}
                    />
                    <p className="text-xs text-muted-foreground">
                      Comma-separated list of websites where the extension should work
                    </p>
                  </div>
                )}

                <div className="flex space-x-3">
                  <Button variant="outline" onClick={() => setStep(1)}>
                    Back
                  </Button>
                  <Button 
                    onClick={handleGenerateExtension}
                    disabled={!selectedType || isGenerating}
                    className="flex-1"
                  >
                    {isGenerating ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                        Generating Extension...
                      </>
                    ) : (
                      <>
                        <Extension className="mr-2 h-4 w-4" />
                        Generate Extension
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Step 3: Download & Install */}
        {step === 3 && generatedExtension && (
          <motion.div
            key="step3"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
          >
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center">
                    <Extension className="h-4 w-4 text-green-600" />
                  </div>
                  <span>Extension Generated Successfully!</span>
                </CardTitle>
                <CardDescription>
                  Your Chrome extension "{generatedExtension.name}" is ready to download and install
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h3 className="font-semibold mb-3">Extension Details</h3>
                    <div className="space-y-2 text-sm">
                      <div><strong>Name:</strong> {generatedExtension.name}</div>
                      <div><strong>Type:</strong> {generatedExtension.extension_type}</div>
                      <div><strong>Status:</strong> 
                        <Badge className="ml-2 bg-green-100 text-green-800">
                          {generatedExtension.status}
                        </Badge>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="font-semibold mb-3">Quick Actions</h3>
                    <div className="space-y-2">
                      <Button onClick={handleDownloadExtension} className="w-full">
                        <Download className="mr-2 h-4 w-4" />
                        Download Extension
                      </Button>
                      <Button variant="outline" className="w-full">
                        <Code className="mr-2 h-4 w-4" />
                        View Code
                      </Button>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="font-semibold mb-3">Installation Instructions</h3>
                  <div className="bg-muted p-4 rounded-lg">
                    <ol className="list-decimal list-inside space-y-2 text-sm">
                      {generatedExtension.install_instructions?.map((instruction: string, index: number) => (
                        <li key={index}>{instruction}</li>
                      ))}
                    </ol>
                  </div>
                </div>

                <div className="flex space-x-3">
                  <Button variant="outline" onClick={() => { setStep(1); setGeneratedExtension(null); }}>
                    Create Another Extension
                  </Button>
                  <Button onClick={handleDownloadExtension} className="flex-1">
                    <Download className="mr-2 h-4 w-4" />
                    Download & Install
                  </Button>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Generation Progress */}
      {isGenerating && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
        >
          <Card className="w-96">
            <CardContent className="p-6 text-center space-y-4">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto" />
              <div>
                <h3 className="font-semibold">Generating Your Extension</h3>
                <p className="text-sm text-muted-foreground">
                  AI agents are working on your Chrome extension...
                </p>
              </div>
              <Progress value={generationProgress} className="w-full" />
              <p className="text-xs text-muted-foreground">
                {generationProgress}% complete
              </p>
            </CardContent>
          </Card>
        </motion.div>
      )}
    </div>
  )
}