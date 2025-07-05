'use client'

import React, { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ChatInterface } from '@/components/chat/chat-interface'
import { CodePreview } from '@/components/preview/code-preview'
import { AppPreview } from '@/components/preview/app-preview'
import { TechStackSelector } from '@/components/forms/tech-stack-selector'
import { ProjectTemplates } from '@/components/templates/project-templates'
import { 
  Sparkles, 
  Code, 
  Zap, 
  Rocket, 
  Brain, 
  Globe,
  Database,
  Cloud,
  Shield,
  Smartphone,
  Chrome
} from 'lucide-react'

export default function HomePage() {
  const [prompt, setPrompt] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [selectedTech, setSelectedTech] = useState<string[]>([])
  const [activeTab, setActiveTab] = useState('prompt')

  const handleGenerate = async () => {
    if (!prompt.trim()) return
    
    setIsGenerating(true)
    try {
      // TODO: Implement AI generation logic
      await new Promise(resolve => setTimeout(resolve, 2000)) // Simulate API call
    } catch (error) {
      console.error('Generation failed:', error)
    } finally {
      setIsGenerating(false)
    }
  }

  const features = [
    {
      icon: Brain,
      title: 'AI-Powered Generation',
      description: 'Advanced AI agents understand your requirements and generate production-ready code'
    },
    {
      icon: Zap,
      title: 'Real-time Preview',
      description: 'See your application come to life instantly with live preview and hot reloading'
    },
    {
      icon: Code,
      title: 'Modern Tech Stack',
      description: 'Built with Next.js 14, TypeScript, Tailwind CSS, and the latest web technologies'
    },
    {
      icon: Database,
      title: 'Full-Stack Ready',
      description: 'Complete backend integration with databases, APIs, and authentication'
    },
    {
      icon: Cloud,
      title: 'Deploy Anywhere',
      description: 'One-click deployment to Vercel, Netlify, AWS, or your preferred platform'
    },
    {
      icon: Shield,
      title: 'Enterprise Grade',
      description: 'Security-first approach with best practices built-in from the start'
    }
  ]

  const quickStarters = [
    { name: 'E-commerce Store', icon: '🛍️', tech: ['Next.js', 'Stripe', 'PostgreSQL'] },
    { name: 'SaaS Dashboard', icon: '📊', tech: ['React', 'Node.js', 'MongoDB'] },
    { name: 'Mobile App', icon: '📱', tech: ['React Native', 'Expo', 'Firebase'] },
    { name: 'AI Chatbot', icon: '🤖', tech: ['Next.js', 'OpenAI', 'Langchain'] },
    { name: 'Crypto DApp', icon: '₿', tech: ['Next.js', 'Web3', 'Solidity'] },
    { name: 'Blog Platform', icon: '📝', tech: ['Next.js', 'MDX', 'Sanity'] }
  ]

  return (
    <div className="container mx-auto space-y-8 p-6">
      {/* Hero Section */}
      <div className="text-center space-y-4">
        <div className="flex items-center justify-center space-x-2">
          <Sparkles className="h-8 w-8 text-agent-primary animate-pulse" />
          <h1 className="text-4xl font-bold bg-gradient-to-r from-agent-primary to-agent-secondary bg-clip-text text-transparent">
            Autonoma AI Webapp Creator
          </h1>
        </div>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
          Transform your ideas into production-ready applications through natural language prompts. 
          Powered by advanced AI agents and modern web technologies.
        </p>
      </div>

      {/* Quick Starters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Rocket className="h-5 w-5" />
            <span>Quick Start Templates</span>
          </CardTitle>
          <CardDescription>Choose a template to get started quickly</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {quickStarters.map((starter) => (
              <Card key={starter.name} className="cursor-pointer hover:shadow-md transition-shadow">
                <CardContent className="p-4 text-center space-y-2">
                  <div className="text-2xl">{starter.icon}</div>
                  <h3 className="font-medium text-sm">{starter.name}</h3>
                  <div className="flex flex-wrap gap-1">
                    {starter.tech.slice(0, 2).map((tech) => (
                      <Badge key={tech} variant="secondary" className="text-xs">
                        {tech}
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Main Interface */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="prompt">Create Webapp</TabsTrigger>
          <TabsTrigger value="extension">Chrome Extension</TabsTrigger>
          <TabsTrigger value="chat">AI Assistant</TabsTrigger>
          <TabsTrigger value="preview">Live Preview</TabsTrigger>
          <TabsTrigger value="deploy">Deploy</TabsTrigger>
        </TabsList>

        <TabsContent value="prompt" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Describe Your Application</CardTitle>
              <CardDescription>
                Tell us what you want to build and our AI agents will create it for you
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label htmlFor="prompt" className="text-sm font-medium">
                  Project Description
                </label>
                <Textarea
                  id="prompt"
                  placeholder="I want to build a modern e-commerce website with user authentication, product catalog, shopping cart, payment processing with Stripe, and an admin dashboard for managing products and orders..."
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  className="min-h-[120px]"
                />
              </div>

              <TechStackSelector 
                selected={selectedTech} 
                onSelectionChange={setSelectedTech} 
              />

              <Button 
                onClick={handleGenerate} 
                disabled={!prompt.trim() || isGenerating}
                className="w-full"
                size="lg"
              >
                {isGenerating ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                    Generating Your App...
                  </>
                ) : (
                  <>
                    <Sparkles className="mr-2 h-4 w-4" />
                    Generate Application
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="extension">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Chrome className="h-6 w-6 text-blue-600" />
                <span>Chrome Extension Generator</span>
              </CardTitle>
              <CardDescription>
                Create powerful Chrome extensions with AI - from popup tools to content scripts
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {[
                  { 
                    name: 'Popup Extension', 
                    desc: 'Quick access toolbar extension',
                    icon: '🔧',
                    complexity: 'Simple',
                    time: '5-15 min'
                  },
                  { 
                    name: 'Content Script', 
                    desc: 'Modify and enhance web pages',
                    icon: '📝',
                    complexity: 'Medium',
                    time: '15-30 min'
                  },
                  { 
                    name: 'Background Service', 
                    desc: 'Background processing extension',
                    icon: '⚙️',
                    complexity: 'Advanced',
                    time: '30-60 min'
                  }
                ].map((type, index) => (
                  <Card key={index} className="cursor-pointer hover:shadow-md transition-shadow">
                    <CardContent className="p-4 text-center space-y-3">
                      <div className="text-3xl">{type.icon}</div>
                      <div>
                        <h3 className="font-semibold">{type.name}</h3>
                        <p className="text-sm text-muted-foreground">{type.desc}</p>
                      </div>
                      <div className="flex justify-between text-xs">
                        <Badge variant="secondary">{type.complexity}</Badge>
                        <span className="text-muted-foreground">{type.time}</span>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>

              <div className="space-y-4">
                <Label htmlFor="extension-prompt">Describe Your Chrome Extension</Label>
                <Textarea
                  id="extension-prompt"
                  placeholder="I want to create a Chrome extension that blocks distracting websites during work hours, shows a productivity timer, and sends notifications when break time starts..."
                  className="min-h-[100px]"
                />
                <Button className="w-full" size="lg">
                  <Chrome className="mr-2 h-4 w-4" />
                  Generate Chrome Extension
                </Button>
              </div>

              <div className="bg-muted p-4 rounded-lg">
                <h4 className="font-medium mb-2">Popular Extension Ideas:</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                  <div>• Password Generator</div>
                  <div>• Website Time Tracker</div>
                  <div>• Social Media Blocker</div>
                  <div>• Page Screenshot Tool</div>
                  <div>• Quick Note Taker</div>
                  <div>• Color Picker</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="chat">
          <ChatInterface />
        </TabsContent>

        <TabsContent value="preview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <CodePreview />
            <AppPreview />
          </div>
        </TabsContent>

        <TabsContent value="deploy">
          <Card>
            <CardHeader>
              <CardTitle>Deploy Your Application</CardTitle>
              <CardDescription>Choose your deployment platform</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {['Vercel', 'Netlify', 'Railway'].map((platform) => (
                  <Card key={platform} className="cursor-pointer hover:shadow-md transition-shadow">
                    <CardContent className="p-6 text-center">
                      <Globe className="h-8 w-8 mx-auto mb-2 text-agent-primary" />
                      <h3 className="font-medium">{platform}</h3>
                      <p className="text-sm text-muted-foreground mt-1">
                        Deploy with one click
                      </p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Features Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {features.map((feature) => (
          <Card key={feature.title} className="agent-card">
            <CardContent className="space-y-3">
              <feature.icon className="h-8 w-8 text-agent-primary" />
              <h3 className="font-semibold">{feature.title}</h3>
              <p className="text-sm text-muted-foreground">{feature.description}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}