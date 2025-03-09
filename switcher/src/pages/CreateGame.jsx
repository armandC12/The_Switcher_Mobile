import React from "react";
import CreateGameForm from "@/components/ui/CreateGameForm";

const CreateGame = () => {
  return (
    <div className="w-full h-screen flex flex-col justify-center items-center bg-zinc-950 px-4 sm:px-8 lg:px-16">
      <h1 className="text-6xl sm:text-5xl lg:text-8xl mb-6 lg:mb-10 text-white text-center">
        Crear partida
      </h1>
      <div className="text-white w-full sm:w-3/4 lg:w-1/3">
        <CreateGameForm />
      </div>
    </div>
  );
};

export default CreateGame;
