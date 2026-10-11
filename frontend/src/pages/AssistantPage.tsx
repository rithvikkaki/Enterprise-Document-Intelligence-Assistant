import React, { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import {
  MessageSquare,
  Send,
  Sparkles,
  User,
  Bot,
  FileText,
  AlertCircle,
  ChevronRight,
  ShieldCheck,
  FolderOpen,
  Copy,
  Check,
  RotateCcw,
  UploadCloud,
  HelpCircle,
} from 'lucide-react';
import MainLayout from '../components/layout/MainLayout';
import { useAuth } from '../context/AuthContext';
import { chatApi } from '../api/chat';
import { projectsApi } from '../api/projects';
import { documentsApi } from '../api/documents';
import { SourceCitation, Project, Document } from '../types';

interface Message {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  sources?: SourceCitation[];
  timestamp: string;
}

export default function AssistantPage() {
  const { activeOrg, activeProject, setActiveProject } = useAuth();

  const [question, setQuestion] = useState('');
  const [selectedProjectId, setSelectedProjectId] = useState<string>(activeProject?.id || '');
  const [messages, setMessages] = useState<Message[]>([]);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { data: projects = [] } = useQuery<Project[]>({
    queryKey: ['projects', activeOrg?.id],
    queryFn: () => projectsApi.list(activeOrg!.id),
    enabled: !!activeOrg,
  });

  const { data: projectDocs = [] } = useQuery<Document[]>({
    queryKey: ['documents', activeOrg?.id, selectedProjectId],
    queryFn: () => documentsApi.list(activeOrg!.id, selectedProjectId),
    enabled: !!activeOrg && !!selectedProjectId,
  });

  useEffect(() => {
    if (projects.length > 0) {
      if (!selectedProjectId || !projects.some((p) => p.id === selectedProjectId)) {
        const projToSelect =
          activeProject?.id && projects.some((p) => p.id === activeProject.id)
            ? activeProject.id
            : projects[0].id;
        setSelectedProjectId(projToSelect);
        const p = projects.find((x) => x.id === projToSelect);
        if (p && (!activeProject || activeProject.id !== p.id)) {
          setActiveProject(p);
        }
      }
    }
  }, [projects, selectedProjectId, activeProject, setActiveProject]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const chatMutation = useMutation({
    mutationFn: async (q: string) => {
      if (!selectedProjectId) throw new Error('Please select a project first.');
      return chatApi.ask(activeOrg!.id, q, selectedProjectId);
    },
    onSuccess: (data) => {
      const assistantMsg: Message = {
        id: `ast_${Date.now()}`,
        sender: 'assistant',
        text: data.answer,
        sources: data.sources,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    },
    onError: (err: any) => {
      const errorMsg: Message = {
        id: `err_${Date.now()}`,
        sender: 'assistant',
        text: `Error generating response: ${
          err.response?.data?.error?.message ||
          'Failed to reach local Ollama inference service. Ensure Ollama is running and model llama3:8b is pulled.'
        }`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, errorMsg]);
    },
  });

  const submitQuestion = (qText: string) => {
    const q = qText.trim();
    if (!q || !selectedProjectId || chatMutation.isPending) return;

    const userMsg: Message = {
      id: `usr_${Date.now()}`,
      sender: 'user',
      text: q,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setQuestion('');
    chatMutation.mutate(q);
  };

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    submitQuestion(question);
  };

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const currentProject = projects.find((p) => p.id === selectedProjectId);

  // Quick suggestions available to click anytime
  const promptSuggestions = [
    '👋 What documents are in this project?',
    '📋 Summarize key findings',
    '🔍 What are the core topics and terms?',
    '💡 Explain the key obligations or specs',
  ];

  // Helper to render bold markdown and clean bullet points
  const renderFormattedContent = (content: string) => {
    const lines = content.split('\n');
    return lines.map((line, idx) => {
      if (!line.trim()) {
        return <div key={idx} className="h-2" />;
      }

      // Format bold segments: **text**
      const parts = line.split(/(\*\*.*?\*\*)/g);
      const renderedLine = parts.map((part, pIdx) => {
        if (part.startsWith('**') && part.endsWith('**')) {
          return (
            <strong key={pIdx} className="font-semibold text-slate-900">
              {part.slice(2, -2)}
            </strong>
          );
        }
        return <span key={pIdx}>{part}</span>;
      });

      if (line.trim().startsWith('•') || line.trim().startsWith('-')) {
        return (
          <div key={idx} className="flex items-start gap-2 my-0.5 ml-1">
            <span className="text-red-500 font-bold leading-relaxed">•</span>
            <span className="flex-1 leading-relaxed">{renderedLine}</span>
          </div>
        );
      }

      return (
        <p key={idx} className="leading-relaxed my-0.5">
          {renderedLine}
        </p>
      );
    });
  };

  return (
    <MainLayout pageTitle="AI Knowledge Assistant">
      <div className="max-w-4xl mx-auto flex flex-col h-[calc(100vh-100px)] sm:h-[calc(100vh-120px)] lg:h-[calc(100vh-140px)]">
        {/* Top bar with project context selector & document status */}
        <div className="bg-white px-3.5 sm:px-5 py-3 sm:py-3.5 rounded-2xl border border-slate-200/90 shadow-card flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-3 shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-xl bg-red-50 text-red-600 flex items-center justify-center shadow-xs shrink-0">
              <Bot size={18} />
            </div>
            <div className="min-w-0 flex-1">
              <h3 className="text-xs sm:text-sm font-bold text-slate-800 flex flex-wrap items-center gap-1.5 sm:gap-2">
                <span className="truncate">Knowledge Assistant</span>
                {projectDocs.length > 0 ? (
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] sm:text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200/70">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                    {projectDocs.length} {projectDocs.length === 1 ? 'doc' : 'docs'}
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] sm:text-[11px] font-medium bg-amber-50 text-amber-700 border border-amber-200/70">
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-500" />
                    0 docs
                  </span>
                )}
              </h3>
              <p className="text-[11px] sm:text-xs text-slate-400 truncate">Hybrid RRF + Groq Cloud LLM</p>
            </div>
          </div>

          <div className="flex items-center justify-between sm:justify-end gap-2 w-full sm:w-auto">
            <div className="flex items-center gap-1.5 sm:gap-2 flex-1 sm:flex-initial">
              <span className="text-[11px] sm:text-xs font-semibold text-slate-500 shrink-0">Project:</span>
              <select
                value={selectedProjectId}
                onChange={(e) => {
                  setSelectedProjectId(e.target.value);
                  const p = projects.find((x) => x.id === e.target.value);
                  if (p) setActiveProject(p);
                }}
                className="py-1 px-2 sm:py-1.5 sm:px-3 border border-slate-200 rounded-xl text-xs bg-white text-slate-700 font-medium focus:ring-2 focus:ring-red-500 focus:outline-none w-full sm:w-auto max-w-[170px] truncate"
              >
                <option value="" disabled>
                  Select a project...
                </option>
                {projects.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name}
                  </option>
                ))}
              </select>
            </div>

            {messages.length > 0 && (
              <button
                onClick={() => setMessages([])}
                title="Clear conversation"
                className="text-xs text-slate-500 hover:text-red-600 px-2.5 py-1.5 rounded-lg border border-slate-200 hover:border-red-200 bg-slate-50 hover:bg-red-50 transition-colors flex items-center gap-1 cursor-pointer"
              >
                <RotateCcw size={12} />
                <span>Reset</span>
              </button>
            )}
          </div>
        </div>

        {/* Empty project warning banner if 0 documents */}
        {selectedProjectId && projectDocs.length === 0 && (
          <div className="mb-3 px-4 py-2.5 bg-amber-50/90 border border-amber-200 rounded-xl text-xs text-amber-800 flex items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <AlertCircle size={15} className="text-amber-600 shrink-0" />
              <span>
                Project <strong>"{currentProject?.name}"</strong> has no indexed documents yet. Upload a document to ask questions!
              </span>
            </div>
            <Link
              to="/documents"
              className="inline-flex items-center gap-1 px-2.5 py-1 bg-amber-600 hover:bg-amber-700 text-white rounded-lg font-semibold text-xs transition-colors shrink-0"
            >
              <UploadCloud size={12} /> Upload
            </Link>
          </div>
        )}

        {/* Message Stream */}
        <div className="flex-1 overflow-y-auto bg-white rounded-2xl border border-slate-200/90 p-3 sm:p-5 lg:p-6 shadow-card space-y-4 sm:space-y-6">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center p-3 sm:p-6 text-slate-400">
              <div className="w-12 h-12 sm:w-14 sm:h-14 rounded-2xl bg-red-50 text-red-600 flex items-center justify-center mb-3 shadow-2xs">
                <Sparkles size={24} />
              </div>
              <h3 className="text-sm sm:text-base font-semibold text-slate-800">
                Interactive Document Assistant
              </h3>
              <p className="text-xs sm:text-sm text-slate-500 max-w-md mt-1 mb-4 sm:mb-5 px-2">
                Ask questions about your uploaded agreements, specifications, policies, or financial reports.
              </p>

              {/* Interactive prompt starter cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 text-left max-w-lg w-full">
                {promptSuggestions.map((sample) => (
                  <button
                    key={sample}
                    onClick={() => submitQuestion(sample)}
                    className="p-3 rounded-xl border border-slate-200 text-xs text-slate-700 hover:border-red-400 hover:bg-red-50/40 hover:text-red-900 transition-colors text-left flex items-start justify-between group cursor-pointer shadow-2xs"
                  >
                    <span>{sample}</span>
                    <ChevronRight size={14} className="text-slate-300 group-hover:text-red-500 shrink-0 mt-0.5" />
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((msg) => {
              const isUser = msg.sender === 'user';
              return (
                <div
                  key={msg.id}
                  className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}
                >
                  {!isUser && (
                    <div className="w-8 h-8 rounded-xl bg-red-50 text-red-700 flex items-center justify-center shrink-0 mt-0.5 shadow-2xs">
                      <Bot size={18} />
                    </div>
                  )}

                  <div className={`max-w-2xl ${isUser ? 'items-end' : 'items-start'}`}>
                    <div
                      className={`p-4 rounded-2xl text-sm leading-relaxed shadow-xs ${
                        isUser
                          ? 'bg-red-600 text-white rounded-br-xs'
                          : 'bg-slate-50/90 border border-slate-200/90 text-slate-800 rounded-bl-xs'
                      }`}
                    >
                      {isUser ? (
                        <p className="whitespace-pre-wrap">{msg.text}</p>
                      ) : (
                        <div>
                          <div className="text-slate-800 text-[13.5px]">
                            {renderFormattedContent(msg.text)}
                          </div>

                          {/* Quick copy button */}
                          <div className="flex items-center justify-end mt-2 pt-2 border-t border-slate-200/60">
                            <button
                              onClick={() => copyToClipboard(msg.text, msg.id)}
                              className="text-[11px] text-slate-400 hover:text-slate-700 flex items-center gap-1 transition-colors cursor-pointer"
                              title="Copy response"
                            >
                              {copiedId === msg.id ? (
                                <>
                                  <Check size={12} className="text-emerald-600" />
                                  <span className="text-emerald-600 font-medium">Copied</span>
                                </>
                              ) : (
                                <>
                                  <Copy size={12} />
                                  <span>Copy</span>
                                </>
                              )}
                            </button>
                          </div>
                        </div>
                      )}

                      {/* Source Citations */}
                      {msg.sources && msg.sources.length > 0 && (
                        <div className="mt-3 pt-3 border-t border-slate-200/80">
                          <p className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2 flex items-center gap-1.5">
                            <ShieldCheck size={14} className="text-emerald-600" />
                            Grounded Citations ({msg.sources.length})
                          </p>
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                            {msg.sources.map((src, i) => (
                              <Link
                                key={src.chunk_id || i}
                                to={`/documents/${src.document_id}`}
                                className="p-2.5 rounded-xl bg-white border border-slate-200 hover:border-red-300 text-xs transition-colors block group shadow-2xs"
                              >
                                <div className="flex items-center justify-between text-slate-800 font-semibold mb-0.5">
                                  <span className="flex items-center gap-1.5 truncate max-w-[170px]">
                                    <FileText size={12} className="text-red-600 shrink-0" />
                                    [{i + 1}] {src.document_name}
                                  </span>
                                  <ChevronRight size={12} className="text-slate-400 group-hover:text-red-600" />
                                </div>
                                <p className="text-[11px] text-slate-500 truncate italic">
                                  "{src.snippet}"
                                </p>
                              </Link>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                    <span className="text-[10px] text-slate-400 mt-1 px-1 block text-right font-medium">
                      {msg.timestamp}
                    </span>
                  </div>

                  {isUser && (
                    <div className="w-8 h-8 rounded-xl bg-slate-200 text-slate-700 flex items-center justify-center shrink-0 mt-0.5">
                      <User size={16} />
                    </div>
                  )}
                </div>
              );
            })
          )}

          {chatMutation.isPending && (
            <div className="flex gap-3 justify-start items-center text-slate-500 text-sm">
              <div className="w-8 h-8 rounded-xl bg-red-50 text-red-700 flex items-center justify-center shrink-0">
                <Bot size={18} />
              </div>
              <div className="p-3.5 bg-slate-50 border border-slate-200/90 rounded-2xl flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-red-600 animate-bounce" />
                <div className="w-2 h-2 rounded-full bg-red-600 animate-bounce [animation-delay:0.2s]" />
                <div className="w-2 h-2 rounded-full bg-red-600 animate-bounce [animation-delay:0.4s]" />
                <span className="text-xs text-slate-600 font-medium ml-1">
                  Searching knowledge base and synthesizing answer...
                </span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Interactive Quick Prompt Chips above input bar */}
        <div className="flex items-center gap-1.5 sm:gap-2 overflow-x-auto py-1.5 sm:py-2 shrink-0 scrollbar-none">
          <span className="text-[10px] sm:text-[11px] font-semibold text-slate-400 uppercase tracking-wider shrink-0 flex items-center gap-1">
            <Sparkles size={11} className="text-red-500" /> Suggestions:
          </span>
          {promptSuggestions.map((prompt) => (
            <button
              key={prompt}
              type="button"
              disabled={chatMutation.isPending || !selectedProjectId}
              onClick={() => submitQuestion(prompt)}
              className="text-[11px] sm:text-xs px-2.5 sm:px-3 py-1 bg-white hover:bg-red-50 text-slate-700 hover:text-red-700 border border-slate-200 hover:border-red-200 rounded-full shrink-0 transition-colors cursor-pointer shadow-2xs disabled:opacity-50"
            >
              {prompt}
            </button>
          ))}
        </div>

        {/* Input Area */}
        <form onSubmit={handleSend} className="flex gap-2 sm:gap-2.5 shrink-0">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            disabled={!selectedProjectId || chatMutation.isPending}
            placeholder={
              selectedProjectId
                ? projectDocs.length > 0
                  ? 'Ask anything about project documents...'
                  : 'Type "hello" or ask a question...'
                : 'Select a project above to start chatting...'
            }
            className="flex-1 px-3.5 sm:px-4 py-2.5 sm:py-3 bg-white border border-slate-200 rounded-xl sm:rounded-2xl text-xs sm:text-sm placeholder-slate-400 text-slate-900 focus:outline-none focus:border-red-500 focus:ring-4 focus:ring-red-500/10 shadow-card disabled:bg-slate-100 disabled:cursor-not-allowed transition-all"
          />
          <button
            type="submit"
            disabled={!question.trim() || !selectedProjectId || chatMutation.isPending}
            className="px-3.5 sm:px-5 py-2.5 sm:py-3 bg-red-600 text-white rounded-xl sm:rounded-2xl text-xs sm:text-sm font-semibold hover:bg-red-700 disabled:opacity-50 transition-colors flex items-center gap-1.5 sm:gap-2 shadow-xs cursor-pointer shrink-0"
          >
            <Send size={15} />
            <span className="hidden sm:inline">Send</span>
          </button>
        </form>
      </div>
    </MainLayout>
  );
}
