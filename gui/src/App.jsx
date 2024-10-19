import { useState } from 'react'

import './App.css'
import Chat from './assets/components/Chat'
import ContextProvider from './assets/context/context'

function App() {

  return (
    <>
    <ContextProvider>
       <Chat/>
    </ContextProvider>
      
    
    </>
  )
}

export default App
