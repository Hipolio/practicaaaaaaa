function activeMenuOption(href) {
    $(".app-menu .nav-link")
    .removeClass("active")
    .removeAttr('aria-current')

    $(`[href="${(href ? href : "#/")}"]`)
    .addClass("active")
    .attr("aria-current", "page")
}

const app = angular.module("angularjsApp", ["ngRoute"])
app.config(function ($routeProvider, $locationProvider) {
    $locationProvider.hashPrefix("")

    $routeProvider
    .when("/", {
        templateUrl: "/app",
        controller: "appCtrl"
    })
    .when("/padrinos", {
        templateUrl: "/padrinos",
        controller: "padrinosCtrl"
    })
    .when("/decoraciones", {
        templateUrl: "/decoraciones",
        controller: "decoracionesCtrl"
    })
    .when("/cargo", {
        templateUrl: "/cargo",
        controller: "cargoCtrl"
    })
    .otherwise({
        redirectTo: "/"
    })
})
app.run(["$rootScope", "$location", "$timeout", function($rootScope, $location, $timeout) {
    function actualizarFechaHora() {
        lxFechaHora = DateTime
        .now()
        .setLocale("es")

        $rootScope.angularjsHora = lxFechaHora.toFormat("hh:mm:ss a")
        $timeout(actualizarFechaHora, 1000)
    }

    $rootScope.slide = ""

    actualizarFechaHora()

    $rootScope.$on("$routeChangeSuccess", function (event, current, previous) {
        $("html").css("overflow-x", "hidden")
        
        const path = current.$$route.originalPath

        if (path.indexOf("splash") == -1) {
            const active = $(".app-menu .nav-link.active").parent().index()
            const click  = $(`[href^="#${path}"]`).parent().index()

            if (active != click) {
                $rootScope.slide  = "animate__animated animate__faster animate__slideIn"
                $rootScope.slide += ((active > click) ? "Left" : "Right")
            }

            $timeout(function () {
                $("html").css("overflow-x", "auto")

                $rootScope.slide = ""
            }, 1000)

            activeMenuOption(`#${path}`)
        }
    })
}])

app.controller("appCtrl", function ($scope, $http) {
    $("#frmInicioSesion").submit(function (event) {
        event.preventDefault()
        $.post("iniciarSesion", $(this).serialize(), function (respuesta) {
            if (respuesta.length) {
                alert("Iniciaste Sesión")
                window.location = "/#/padrinos"

                return
            }

            alert("Usuario y/o Contraseña Incorrecto(s)")
        })
    })
})
app.controller("padrinosCtrl", function ($scope, $http) {
    function buscarPadrinos() {
        $.get("/tbodyPadrinos", function (trsHTML) {
            $("#tbodyPadrinos").html(trsHTML)
        })
    }

    buscarPadrinos()
    
    // Enable pusher logging - don't include this in production
    Pusher.logToConsole = true

    var pusher = new Pusher("fd4071018e972df38f9a", {
      cluster: "us2"
    })

    var channel = pusher.subscribe("hardy-drylands-461")
    channel.bind("eventoPadrinos", function(data) {
        buscarPadrinos()
    })

    $(document).on("submit", "#frmPadrino", function (event) {
        event.preventDefault()

        $.post("/padrino", {
            idPadrino: "",
            nombrePadrino:     $("#txtNombrePadrino").val(),
            sexo:              $("#txtSexo").val(),
            telefono:          $("#txtTelefono").val(),
            correoElectronico: $("#txtEmail").val(),
        })
    })

    $(document).off("click", ".btn-eliminar").on("click", ".btn-eliminar", function () {
        const id = $(this).data("idpadrino")

        if (!confirm("¿Seguro que deseas eliminar este padrino?")) {
            return
        }

        $.post("/padrino/eliminar", { idPadrino: id }, function () {
            buscarPadrinos()
        }).fail(function(xhr) {
            alert("Error al eliminar: " + xhr.responseText)
        })
    })
})

app.controller("decoracionesCtrl", function ($scope, $http) {
    function buscarDecoraciones() {
        $.get("/tbodyDecoraciones", function (trsHTML) {
            $("#tbodyDecoraciones").html(trsHTML)
        })
    }

    buscarDecoraciones()
    
    Pusher.logToConsole = true

    var pusher = new Pusher("e57a8ad0a9dc2e83d9a2", {
      cluster: "us2"
    })

    var channel = pusher.subscribe("canalDecoraciones")
    channel.bind("eventoDecoraciones", function(data) {
        buscarDecoraciones()
    })

    $(document).on("submit", "#frmDecoracion", function (event) {
        event.preventDefault()

        $.post("/decoracion", {
            id: "",
            nombre: $("#txtNombre").val(),
            precio: $("#txtPrecio").val(),
            existencias: $("#txtExistencias").val(),
        })
    })
})

// === NUEVO CONTROLADOR PARA CARGOS ===
app.controller("cargoCtrl", function ($scope, $http) {
    function buscarCargo() {
        $.get("/tbodyCargo", function (trsHTML) {
            $("#tbodyCargo").html(trsHTML)
        })
    }

    buscarCargo()
    
    Pusher.logToConsole = true

    var pusher = new Pusher("57413b779fac9cbb46c7", {
      cluster: "us2"
    })

    var channel = pusher.subscribe("canalCargo")
    channel.bind("eventoCargo", function(data) {
        buscarCargo()
    })

    $(document).on("submit", "#frmCargo", function (event) {
        event.preventDefault()

        $.post("/cargo", {
            idCargo: "",
            descripcion: $("#txtDescripcion").val(),
            monto:       $("#txtMonto").val(),
            fecha:       $("#txtFecha").val(),
            idMascotas:  $("#txtIdMascota").val(),
        })
    })

    $(document).off("click", ".btn-eliminar").on("click", ".btn-eliminar", function () {
        const id = $(this).data("idcargo")

        if (!confirm("¿Seguro que deseas eliminar este cargo?")) {
            return
        }

        $.post("/cargo/eliminar", { idCargo: id }, function () {
            buscarCargo()
        }).fail(function(xhr) {
            alert("Error al eliminar: " + xhr.responseText)
        })
    })
     // --- editar ---
    $(document).on("click", ".btn-editar", function () {
        const id = $(this).data("id");

        $.get("/cargo/" + id, function (respuesta) {
            if (respuesta.length > 0) {
                const cargo = respuesta[0];
                $("#idCargo").val(cargo.idCargo);
                $("#descripcion").val(cargo.descripcion);
                $("#monto").val(cargo.monto);
                $("#fecha").val(cargo.fecha);
                $("#idMascostas").val(cargo.idMascotas);
            }
        })
    })

    // --- guardar (insertar o actualizar) ---
    $(document).on("submit", "#frmCargo", function (event) {
        event.preventDefault();

        $.post("/cargo", {
            idCargo: $("#idCargo").val(),
            descripcion: $("#descripcion").val(),
            monto: $("#monto").val(),
            fecha: $("#fecha").val(),
            idMascotas: $("#idMascotas").val(),
        }, function () {
            buscarCargo();
            $("#frmCargo")[0].reset();
            $("#idCargo").val("");
        }).fail(function(xhr) {
            alert("Error al guardar: " + xhr.responseText);
        });
    });
})

const DateTime = luxon.DateTime
let lxFechaHora

document.addEventListener("DOMContentLoaded", function (event) {
    const configFechaHora = {
        locale: "es",
        weekNumbers: true,
        minuteIncrement: 15,
        altInput: true,
        altFormat: "d/F/Y",
        dateFormat: "Y-m-d",
    }

    activeMenuOption(location.hash)
})










