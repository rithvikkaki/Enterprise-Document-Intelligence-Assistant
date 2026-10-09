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
} from 'lucide-react';
import MainLayout from '../components/layout/MainLayout';
import { useAuth } from '../context/AuthContext';
import { chatApi } from '../api/chat';
import { projectsApi } from '../api/projects';
import { SourceCitation, Project } from '../types';

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
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { data: projects = [] } = useQuery<Project[]>({
    queryKey: ['projects', activeOrg?.id],
    queryFn: () => projectsApi.list(activeOrg!.id),
    enabled: !!activeOrg,
  });

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

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    const q = question.trim();
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

  return (
    <MainLayout pageTitle="AI Knowledge Assistant">
      <div className="max-w-4xl mx-auto flex flex-col h-[calc(100vh-130px)]">
        {/* Top bar with project selector */}
        <div className="bg-white px-4 py-3 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between mb-4 shrink-0">
          <div className="flex items-center gap-2">
            <Bot className="text-sky-600" size={20} />
            <div>
              <h3 className="text-sm font-bold text-slate-800">Local RAG Document Assistant</h3>
              <p className="text-xs text-slate-400">Grounded by Ollama + Hybrid Reciprocal Rank Fusion</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-500 font-medium">Knowledge Scope:</span>
            <select
              value={selectedProjectId}
              onChange={(e) => {
                setSelectedProjectId(e.target.value);
                const p = projects.find((x) => x.id === e.target.value);
                if (p) setActiveProject(p);
              }}
              className="py-1 px-2.5 border border-slate-200 rounded-lg text-xs bg-white text-slate-700 font-medium focus:ring-2 focus:ring-sky-500 focus:outline-none"
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
        </div>

        {/* Message Stream */}
        <div className="flex-1 overflow-y-auto bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-6">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center p-8 text-slate-400">
              <div className="w-14 h-14 rounded-2xl bg-sky-50 text-sky-600 flex items-center justify-center mb-3">
                <Sparkles size={28} />
              </div>
              <h3 className="text-base font-semibold text-slate-800">
                Ask your organization's documents
              </h3>
              <p className="text-sm text-slate-500 max-w-md mt-1 mb-6">
                Pose queries about uploaded agreements, technical specifications, policies, or financial reports.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-left max-w-lg w-full">
                {[
                  'What are the termination terms in the contract?',
                  'Summarize key findings from the Q3 report',
                  'What are the vacation and leave rules?',
                  'Explain the data security procedures',
                ].map((sample) => (
                  <button
                    key={sample}
                    onClick={() => {
                      if (selectedProjectId) {
                        setQuestion(sample);
                      } else {
                        alert('Please select a project first.');
                      }
                    }}
                    className="p-2.5 rounded-xl border border-slate-200 text-xs text-slate-600 hover:border-sky-500 hover:bg-sky-50/50 transition-colors text-left"
                  >
                    "{sample}"
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
                    <div className="w-8 h-8 rounded-full bg-sky-100 text-sky-700 flex items-center justify-center shrink-0 mt-0.5">
                      <Bot size={18} />
                    </div>
                  )}

                  <div className={`max-w-2xl ${isUser ? 'items-end' : 'items-start'}`}>
                    <div
                      className={`p-4 rounded-2xl text-sm leading-relaxed shadow-sm ${
                        isUser
                          ? 'bg-sky-600 text-white rounded-br-xs'
                          : 'bg-slate-50 border border-slate-200 text-slate-800 rounded-bl-xs'
                      }`}
                    >
                      <p className="whitespace-pre-wrap">{msg.text}</p>

                      {/* Source Citations */}
                      {msg.sources && msg.sources.length > 0 && (
                        <div className="mt-4 pt-3 border-t border-slate-200/80">
                          <p className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2 flex items-center gap-1">
                            <ShieldCheck size={14} className="text-emerald-600" />
                            Grounded Source Citations ({msg.sources.length})
                          </p>
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                            {msg.sources.map((src, i) => (
                              <Link
                                key={src.chunk_id || i}
                                to={`/documents/${src.document_id}`}
                                className="p-2 rounded-lg bg-white border border-slate-200 hover:border-sky-500 text-xs transition-colors block group"
                              >
                                <div className="flex items-center justify-between text-slate-700 font-semibold mb-0.5">
                                  <span className="flex items-center gap-1 truncate max-w-[170px]">
                                    <FileText size={12} className="text-sky-600 shrink-0" />
                                    [{i + 1}] {src.document_name}
                                  </span>
                                  <ChevronRight size={12} className="text-slate-400 group-hover:text-sky-600" />
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
                    <span className="text-[10px] text-slate-400 mt-1 px-1 block text-right">
                      {msg.timestamp}
                    </span>
                  </div>

                  {isUser && (
                    <div className="w-8 h-8 rounded-full bg-slate-200 text-slate-700 flex items-center justify-center shrink-0 mt-0.5">
                      <User size={16} />
                    </div>
                  )}
                </div>
              );
            })
          )}

          {chatMutation.isPending && (
            <div className="flex gap-3 justify-start items-center text-slate-500 text-sm">
              <div className="w-8 h-8 rounded-full bg-sky-100 text-sky-700 flex items-center justify-center shrink-0">
                <Bot size={18} />
              </div>
              <div className="p-3 bg-slate-50 border border-slate-200 rounded-2xl flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-sky-600 animate-bounce" />
                <div className="w-2 h-2 rounded-full bg-sky-600 animate-bounce [animation-delay:0.2s]" />
                <div className="w-2 h-2 rounded-full bg-sky-600 animate-bounce [animation-delay:0.4s]" />
                <span className="text-xs text-slate-500 font-medium ml-1">
                  Synthesizing answer from retrieved chunks...
                </span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <form onSubmit={handleSend} className="mt-3 flex gap-2 shrink-0">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            disabled={!selectedProjectId || chatMutation.isPending}
            placeholder={
              selectedProjectId
                ? 'Ask a question about your project documents...'
                : 'Select a project above to start chatting...'
            }
            className="flex-1 px-4 py-3 border border-slate-300 rounded-xl text-sm placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent bg-white shadow-sm disabled:bg-slate-100 disabled:cursor-not-allowed"
          />
          <button
            type="submit"
            disabled={!question.trim() || !selectedProjectId || chatMutation.isPending}
            className="px-5 py-3 bg-sky-600 text-white rounded-xl text-sm font-medium hover:bg-sky-700 disabled:opacity-50 transition-colors flex items-center gap-2 shadow-sm cursor-pointer"
          >
            <Send size={16} />
            <span>Send</span>
          </button>
        </form>
      </div>
    </MainLayout>
  );
}
