import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables')
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true
  },
  realtime: {
    params: {
      eventsPerSecond: 10
    }
  }
})

// Auth helpers
export const auth = {
  // Sign up
  signUp: async (email: string, password: string, fullName?: string) => {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: {
          full_name: fullName
        }
      }
    })
    return { data, error }
  },

  // Sign in
  signIn: async (email: string, password: string) => {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password
    })
    return { data, error }
  },

  // Sign out
  signOut: async () => {
    const { error } = await supabase.auth.signOut()
    return { error }
  },

  // Get current user
  getCurrentUser: async () => {
    const { data: { user }, error } = await supabase.auth.getUser()
    return { user, error }
  },

  // Get session
  getSession: async () => {
    const { data: { session }, error } = await supabase.auth.getSession()
    return { session, error }
  },

  // Listen to auth changes
  onAuthStateChange: (callback: (event: string, session: any) => void) => {
    return supabase.auth.onAuthStateChange(callback)
  }
}

// Database helpers
export const db = {
  // Documents
  documents: {
    // Get all documents for current user
    getAll: async (userId: string) => {
      const { data, error } = await supabase
        .from('documents')
        .select('*')
        .eq('user_id', userId)
        .order('created_at', { ascending: false })
      return { data, error }
    },

    // Get single document
    getById: async (id: string) => {
      const { data, error } = await supabase
        .from('documents')
        .select('*')
        .eq('id', id)
        .single()
      return { data, error }
    },

    // Create document
    create: async (document: any) => {
      const { data, error } = await supabase
        .from('documents')
        .insert(document)
        .select()
        .single()
      return { data, error }
    },

    // Update document
    update: async (id: string, updates: any) => {
      const { data, error } = await supabase
        .from('documents')
        .update(updates)
        .eq('id', id)
        .select()
        .single()
      return { data, error }
    },

    // Delete document
    delete: async (id: string) => {
      const { error } = await supabase
        .from('documents')
        .delete()
        .eq('id', id)
      return { error }
    }
  },

  // Search
  search: {
    // Semantic search using pgvector
    semantic: async (queryEmbedding: number[], threshold: number = 0.7, limit: number = 20) => {
      const { data, error } = await supabase.rpc('semantic_search', {
        query_embedding: queryEmbedding,
        similarity_threshold: threshold,
        match_count: limit
      })
      return { data, error }
    },

    // Hybrid search
    hybrid: async (queryText: string, queryEmbedding: number[], threshold: number = 0.7, limit: number = 20) => {
      const { data, error } = await supabase.rpc('hybrid_search', {
        query_text: queryText,
        query_embedding: queryEmbedding,
        similarity_threshold: threshold,
        match_count: limit
      })
      return { data, error }
    }
  },

  // User queries (chat history)
  queries: {
    // Get chat history
    getHistory: async (userId: string) => {
      const { data, error } = await supabase
        .from('user_queries')
        .select('*')
        .eq('user_id', userId)
        .order('created_at', { ascending: false })
      return { data, error }
    },

    // Save query
    save: async (query: any) => {
      const { data, error } = await supabase
        .from('user_queries')
        .insert(query)
        .select()
        .single()
      return { data, error }
    }
  }
}

// Real-time subscriptions
export const realtime = {
  // Subscribe to document changes
  subscribeToDocuments: (userId: string, callback: (payload: any) => void) => {
    return supabase
      .channel('documents')
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'documents',
          filter: `user_id=eq.${userId}`
        },
        callback
      )
      .subscribe()
  },

  // Subscribe to processing status
  subscribeToProcessing: (documentId: string, callback: (payload: any) => void) => {
    return supabase
      .channel(`processing-${documentId}`)
      .on(
        'postgres_changes',
        {
          event: 'UPDATE',
          schema: 'public',
          table: 'documents',
          filter: `id=eq.${documentId}`
        },
        callback
      )
      .subscribe()
  }
}

export default supabase
