FROM mcr.microsoft.com/dotnet/sdk:8.0.416
WORKDIR /App
COPY . ./
RUN dotnet restore
CMD [ "dotnet", "run" ]
