import React, { useRef, useState, useEffect } from 'react'
import { useSocketContext } from '@/context/SocketContext';
import { useGameContext } from '@/context/GameContext';
import { useChatSocket } from '../hooks/use-chat-socket';
import { Button } from './button';
import { ScrollArea } from "@/components/ui/scroll-area"
import { IoIosSend, IoIosChatboxes } from "react-icons/io";
import { FaMinus } from "react-icons/fa";
import { motion, AnimatePresence } from 'framer-motion';

const colors = ["bg-red-500", "bg-blue-500", "bg-green-500", "bg-yellow-500"];


export default function Chat({ gameId, lobby }) {
  const [message, setMessage] = useState('');
  const [chat, setChat] = useState([]);
  const { socket } = useSocketContext();
  const { username, players } = useGameContext();
  const [isMinimized, setIsMinimized] = useState(true);
  const [shouldAutoScroll, setShouldAutoScroll] = useState(true);
  const [newMessageReceived, setNewMessageReceived] = useState(false);
  const viewportRef = useRef(null);

  const getPlayerColor = (index) => {
    return colors[index % colors.length];
  };

  const handleChatClick = () => {
    setIsMinimized(false);
    setShouldAutoScroll(true);
    setNewMessageReceived(false); // Reset new message indicator when chat is opened
  };

  const handleScroll = () => {
    const viewport = viewportRef.current;
    if (!viewport) return;
    const position = viewport.scrollTop + viewport.clientHeight;
    const height = viewport.scrollHeight;
    const enableAutoScroll = height - position <= 50;
    enableAutoScroll ? setShouldAutoScroll(true) : setShouldAutoScroll(false);
  };

  useEffect(() => {
    if (!isMinimized) {
      const viewport = document.querySelector('[data-radix-scroll-area-viewport]');
      if (viewport) {
        viewportRef.current = viewport;
        viewport.addEventListener('scroll', handleScroll);
      }
    }
    return () => {
      if (viewportRef.current) viewportRef.current.removeEventListener('scroll', handleScroll);
    };
  }, [isMinimized]);

  useEffect(() => {
    if (!viewportRef.current || !shouldAutoScroll) return;
    viewportRef.current.scrollTop = viewportRef.current.scrollHeight;
  }, [chat, isMinimized]);

  const handleSendMessage = (e) => {
    e?.preventDefault();
    if (message.trim()) {
      const formattedMessage = `${username}: ${message}`;
      const formattedType = `${gameId}:CHAT_MESSAGE`;
      socket.send(JSON.stringify({
        type: formattedType,
        message: formattedMessage
      }));
    }
    setMessage('');
  };

  useChatSocket(gameId, chat, setChat);

  useEffect(() => {
    if (isMinimized && chat.length > 0) {
      setNewMessageReceived(true);
      const timer = setTimeout(() => setNewMessageReceived(false), 7000);
      return () => clearTimeout(timer); // Clear timeout on component unmount or new message
    }
  }, [chat, isMinimized]);


  return (
    <>
    {
      lobby ? 
      <AnimatePresence>
      {!isMinimized ? (
        <motion.div
          className="w-full md:w-[32rem] max-w-[32rem] bg-zinc-900 p-4 rounded-lg shadow-md border border-zinc-800"
          key="expanded"
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          transition={{ duration: 0.25 }}
        >
          {/* Chat Header */}
          <div className="flex items-center justify-between p-2 border-b border-zinc-800">
            <h3 className="text-3xl text-white">Chat</h3>
            <Button
              onClick={() => setIsMinimized(true)}
              className="text-zinc-400 hover:text-white transition-colors p-1 rounded-lg hover:bg-zinc-800"
            >
              <FaMinus />
            </Button>
          </div>

          {/* Chat Messages */}
          <ScrollArea id='chatScrollArea' className="h-80 mb-2 pr-3">
            {chat.map((msg, index) => {
              const isChatMessage = msg.includes(':');
              const sender = msg.split(':')[0];
              const msgContent = msg.split(':')[1];
              const playerIndex = players.findIndex((player) => player.name === sender);
              const isCurrentUser = sender === username;
              const showSender = index === 0 || (sender !== chat[index - 1].split(':')[0]);

              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.2 }}
                  className={`flex ${isCurrentUser ? 'justify-end' : 'justify-start'} mb-1`}
                >
                  <div className="text-zinc-300 rounded-lg max-w-[85%]">
                    {isChatMessage && showSender && (
                      <span className="text-sm,md text-zinc-400 block mb-3">
                        {!isCurrentUser ? sender : "Tú"}
                      </span>
                    )}
                    <p className={`text-white rounded-lg break-words sm,md:text-sm,md md:text-lg p-2 m-1 ${getPlayerColor(playerIndex)}`}>
                      {msgContent || msg}
                    </p>
                  </div>
                </motion.div>
              );
            })}
          </ScrollArea>

          {/* Message Input */}
          <form onSubmit={handleSendMessage} className='flex items-stretch'>
            <input
              type="text"
              className="flex-1 bg-zinc-800 text-white rounded-l-full px-4 py-2 focus:outline-none"
              placeholder="Escribe tu mensaje..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
            />
            <Button
              type="submit"
              className="rounded-r-full p-3 bg-gray-500 hover:bg-gray-700 transition-colors h-auto"
            >
              <IoIosSend className='w-5 h-5'/>
            </Button>
          </form>
        </motion.div>
      ) : (
        <motion.div
          key="minimized"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.25 }}
        >
          <Button
            onClick={handleChatClick}
            className="w-full md:w-[32rem] p-4 justify-between hover:bg-zinc-800 rounded-lg bg-zinc-900 border border-zinc-800"
          >
            <div className="flex items-center gap-2 overflow-hidden">
              <IoIosChatboxes className="w-5 h-5 shrink-0" />
              <span className="sm,md:text-sm,md md:text-lg truncate">
                {newMessageReceived ? chat[chat.length - 1] : " Abrir chat"}
              </span>
            </div>
          </Button>
        </motion.div>
      )}
    </AnimatePresence> 
    
    : // ACTIVE GAMES CHAT

      <AnimatePresence>
      {!isMinimized ? (
        <motion.div
          className="absolute bottom-20 right-0 bg-opacity-80 bg-zinc-900 z-50 w-full sm,md:w-[600px] p-4 rounded-lg shadow-md border border-zinc-800"
          key="expanded"
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          transition={{ duration: 0.25 }}
        >
          <div className="flex items-center justify-between p-2 border-b border-zinc-800">
          <h3 className="text-2xl text-white">Chat</h3>
            <Button
              onClick={() => setIsMinimized(true)}
              className="text-zinc-400 hover:text-white transition-colors p-1 rounded-lg hover:bg-zinc-800"
            >
              <FaMinus />
            </Button>
          </div>

          <ScrollArea id='chatScrollArea' className="h-80 mb-2 pr-3">
            {chat.map((msg, index) => {
              const isChatMessage = msg.includes(':');
              const sender = msg.split(':')[0];
              const msgContent = msg.split(':')[1];
              const playerIndex = players.findIndex((player) => player.name === sender);
              const isCurrentUser = sender === username;
              const showSender = index===0 || (sender !== chat[index-1].split(':')[0])

              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.2 }}
                  className={`flex ${isCurrentUser ? 'justify-end' : 'justify-start'} mb-1`}
                >
                  <div
                    className={`text-zinc-300 rounded-lg max-w-[85%] 
                      `}
                      >
                    {isChatMessage && showSender && (
                        <span className="text-sm,md text-zinc-400 block mb-3">
                          {!isCurrentUser ? sender : "Tú"}
                        </span>
                      )}
                    
                    <p className={`text-white  rounded-lg break-words sm,md:text-sm,md md:text-lg p-2 m-1 ${getPlayerColor(playerIndex)}`}>
                      {msgContent || msg}
                    </p>
                  </div>
                </motion.div>
              );
            })}
          </ScrollArea>

          <form onSubmit={handleSendMessage} className=' flex items-stretch'>
            <input
              type="text"
              className="flex-1 bg-zinc-800 text-white rounded-l-full px-4 py-2 focus:outline-none"
              placeholder="Escribe tu mensaje..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
            />
            <Button
              type="submit"
              className="rounded-r-full p-3 bg-gray-500 hover:bg-gray-700 transition-colors h-auto"
            >
              <IoIosSend className='w-5 h-5'/>
            </Button>
          </form>
        </motion.div>
      ) : (
        <motion.div
          className='mb-2 w-fit absolute bottom-80 right-2 sm,md:bottom-20 sm,md:right-0 md:bottom-20 md:right-0 bg-zinc-950 bg-opacity-80 hover:bg-zinc-950 '
          key="minimized"
          initial={{ opacity: 0, y: 20}}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.25 }}
        >
          {/* <Button
            onClick={handleChatClick}
            className="w-full p-2 sm,md:p-4 justify-end rounded-lg bg-zinc-950"
          >
            <div className="flex items-center gap-2 overflow-hidden">
              <span className="sm,md:text-sm,md sm,md:text-lg truncate">
                {newMessageReceived ? (chat[chat.length - 1]) : "Abrir chat"}
              </span>
              <IoIosChatboxes className="w-5 h-5 shrink-0 ml-0" />
            </div>
          </Button> */}
          <Button
            onClick={handleChatClick}
            className="flex flex-growp w-full p-2 sm,md:p-4 md:p-4 justify-end rounded-lg bg-zinc-950 flex items-center gap-2"
          >
            <IoIosChatboxes className="w-8 h-8 sm,md:w-5 sm,md:h-5 shrink-0 ml-0" />

            {/* Ocultar texto en pantallas pequeñas, mostrar en pantallas grandes */}
            <span className="hidden sm,md:inline text-sm,md text-white">
              Abrir chat
            </span>
          </Button>
        </motion.div>
      )}
    </AnimatePresence>

    }
    </>
    
  );
};
