import React from 'react';
import NameForm from '../components/ui/NameForm';
import logo from '../assets/logo_switcher.png';

const Home = () => {
  return (
    <div className="w-screen h-screen flex flex-col sm:flex-row">
      {/* Sección Izquierda: Logo y Título */}
      <div className="w-full h-full sm:w-1/2 sm:w-3/4 bg-zinc-950 flex flex-col items-center justify-center p-6">
        <div className="h-full w-full sm:w-auto sm:ml-72 flex flex-col justify-center items-center">
          <h1 className="text-6xl sm:text-6xl lg:text-9xl text-white text-center">
            EL SWITCHER
          </h1>
          <img 
            className="h-60 w-60 mt-6 sm:mt-0.5 sm:h-80 sm:w-80 object-contain" 
            src={logo} 
            alt="Switcher Logo" 
          />
        </div>
      </div>

      {/* Sección Derecha: Formulario */}
      <div className="w-full h-full sm:w-1/2 bg-zinc-950 flex flex-col items-center sm:items-start justify-center p-6">
        <div className="w-full h-full sm:h-auto sm:w-3/4 lg:w-2/3 xl:w-1/2 max-w-lg sm:ml-10">
          <h1 className="text-3xl sm:text-5xl font-bold mb-6 text-white text-center">
            ¡A jugar!
          </h1>
          <NameForm />
        </div>
      </div>
    </div>
  );
};

export default Home;
